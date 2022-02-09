from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Dict, List, Sequence, Tuple, Union
    from uuid import UUID

from .resource import Resource
from spyke.enums import SizedInternalFormat, MagFilter, MinFilter, SwizzleMask, SwizzleTarget, WrapMode, TextureFormat
from spyke.exceptions import SpykeException
from spyke.graphics.texturing import TextureData, TextureSpec, Texture
from spyke.graphics.rectangle import Rectangle
from spyke.graphics import Glyph
from spyke import debug, utils
import time
import numpy as np
import freetype as ft
import glm
import math
from dataclasses import dataclass


@dataclass
class _CharPrototype:
    char: str
    data: np.ndarray
    width: int
    height: int
    left: int
    top: int
    advance: int


class Font(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture
        self.glyphs: Dict[str, Glyph] = {}
        self.base_size: int = 0
        self.name: str = ''

    def _get_all_characters(self, face: ft.Face) -> List[str]:
        return [chr(idx) for _, idx, in face.get_chars() if chr(idx).isprintable()] + ['\n', ]

    def _load_char_data(self, char: str, face: ft.Face, stroker: ft.Stroker) -> _CharPrototype:
        face.load_char(char, ft.FT_LOAD_TARGET_NORMAL |
                       ft.FT_LOAD_NO_BITMAP | ft.FT_LOAD_FORCE_AUTOHINT)

        stroke_glyph = face.glyph.get_glyph()
        stroke_glyph.stroke(stroker, True)
        stroke_glyph_r = stroke_glyph.to_bitmap(
            ft.FT_RENDER_MODE_NORMAL, 0, True)
        stroke_bitmap = stroke_glyph_r.bitmap

        stroker.rewind()

        origin_x = stroke_glyph_r.left
        origin_y = stroke_glyph_r.top

        width_stroke = stroke_bitmap.width
        height_stroke = stroke_bitmap.rows

        data = np.array(stroke_bitmap.buffer, dtype=np.uint8, copy=True).reshape(
            height_stroke, width_stroke)

        fill_glyph = face.glyph.get_glyph()
        fill_glyph_r = fill_glyph.to_bitmap(ft.FT_RENDER_MODE_NORMAL, 0, True)
        fill_bitmap = fill_glyph_r.bitmap

        width_fill = fill_bitmap.width
        height_fill = fill_bitmap.rows

        start_x = ((width_stroke - width_fill) / 2)
        start_y = ((height_stroke - height_fill) / 2)

        start_x = math.floor(start_x)
        start_y = math.floor(start_y)

        data_fill = np.array(fill_bitmap.buffer, dtype=np.uint8, copy=True).reshape(
            height_fill, width_fill)

        for y in range(height_fill):
            for x in range(width_fill):
                data[y + start_y, x + start_x] = max(
                    data[y + start_y, x + start_x], data_fill[y, x])

        prototype = _CharPrototype(
            char, data, width_stroke, height_stroke, origin_x, origin_y, face.glyph.advance.x >> 6)

        return prototype

    def _determine_atlas_size(self, chars_data: Sequence[_CharPrototype], cols: int) -> Tuple[int, int, List[int]]:
        atlas_width = 0
        rows_heights: List[int] = list()

        current_width = 0
        current_height = 0
        current_col = 0
        for char_data in chars_data:
            if current_col >= cols:
                rows_heights.append(current_height)
                atlas_width = max(atlas_width, current_width)
                current_height = 0
                current_width = 0
                current_col = 0

            current_width += char_data.width
            current_height = max(current_height, char_data.height)

            current_col += 1

        rows_heights.append(current_height)
        atlas_width = max(atlas_width, current_width)
        atlas_height = sum(rows_heights)

        return (atlas_width, atlas_height, rows_heights)

    def _load(self, *, size: int = 64, **_) -> None:
        self.base_size = size

        face = ft.Face(self.filepath)
        assert face.is_scalable, 'Cannot load non scalable fonts'
        face.set_pixel_sizes(0, self.base_size)

        self.name = face.family_name.decode('utf-8')

        stroker = ft.Stroker()
        stroker.set(size, ft.FT_STROKER_LINECAP_ROUND,
                    ft.FT_STROKER_LINEJOIN_ROUND, 0)

        chars = self._get_all_characters(face)
        to_combine: Dict[str, _CharPrototype] = dict()
        for char in chars:
            to_combine[char] = self._load_char_data(char, face, stroker)

        cols = max(utils.get_closest_factors(len(chars)))

        atlas_width, atlas_height, rows_heights = self._determine_atlas_size(
            to_combine.values(), cols)

        atlas_width += cols
        atlas_height += len(rows_heights)

        atlas = np.zeros(
            (atlas_height, atlas_width), dtype=np.uint8)

        cur_x = 0
        cur_y = 0
        for char_data in to_combine.values():
            width = char_data.width
            height = char_data.height

            if cur_x + width > atlas_width:
                cur_x = 0
                cur_y += rows_heights.pop(0) + 1

            atlas[cur_y:cur_y + height,
                  cur_x:cur_x + width] = char_data.data

            tex_x = cur_x / atlas_width
            tex_y = cur_y / atlas_height
            tex_width = width / atlas_width
            tex_height = height / atlas_height

            tex_rect = Rectangle(tex_x, tex_y, tex_width, tex_height)
            glyph_obj = Glyph(glm.ivec2(width, height), glm.ivec2(
                char_data.left, char_data.top), char_data.advance, tex_rect)

            self.glyphs[char_data.char] = glyph_obj

            cur_x += width + 1

        texture_data = TextureData()
        texture_data.width = atlas_width
        texture_data.height = atlas_height
        texture_data.data = atlas

        texture_spec = TextureSpec()
        texture_spec.format = TextureFormat.Red
        texture_spec.internal_format = SizedInternalFormat.R8
        texture_spec.mipmaps = 1
        texture_spec.min_filter = MinFilter.Linear
        texture_spec.mag_filter = MagFilter.Linear
        texture_spec.wrap_mode = WrapMode.ClampToEdge
        texture_spec.pixel_alignment = 1
        texture_spec.texture_swizzle = SwizzleTarget.TextureSwizzleRgba
        texture_spec.swizzle_mask = [
            SwizzleMask.One, SwizzleMask.One, SwizzleMask.One, SwizzleMask.Red]

        self._loading_data['texture_spec'] = texture_spec
        self._loading_data['texture_data'] = texture_data

    def _finalize(self) -> None:
        self.texture = Texture(
            self._loading_data['texture_data'], self._loading_data['texture_spec'])

        debug.log_info(
            f'Font from file "{self.filepath}" loaded in {time.perf_counter() - self._loading_start} seconds.')

    def _unload(self) -> None:
        self.texture.delete()

    def get_glyph(self, char: str) -> Glyph:
        if char not in self.glyphs:
            return self.glyphs['\n']

        return self.glyphs[char]
