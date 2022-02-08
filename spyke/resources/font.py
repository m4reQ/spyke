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

        # create stroke bitmap
        stroke_glyph = face.glyph.get_glyph()
        stroke_glyph.stroke(stroker, True)
        stroke_glyph_r = stroke_glyph.to_bitmap(
            ft.FT_RENDER_MODE_NORMAL, 0, True)
        stroke_bitmap = stroke_glyph_r.bitmap

        # return stroker to its begin state
        stroker.rewind()

        # create buffer for combined bitmaps and copy stroke bitmap
        c_x = stroke_bitmap.width
        c_y = stroke_bitmap.rows
        o_x = stroke_glyph_r.left
        o_y = stroke_glyph_r.top

        buffer = np.zeros((c_x * c_y * 2,), dtype=np.uint8)

        # NOTE: This operation is very slow though we should
        # consider using some numpy functions for it
        stroke_buffer = stroke_bitmap.buffer
        for i in range(c_x * c_y):
            # copy every pixel to the second channel
            buffer[i * 2 + 1] = stroke_buffer[i]

        # load filled glyph
        fill_glyph = face.glyph.get_glyph()
        fill_glyph_r = fill_glyph.to_bitmap(ft.FT_RENDER_MODE_NORMAL, 0, True)
        fill_bitmap = fill_glyph_r.bitmap

        c_x_fill = fill_bitmap.width
        c_y_fill = fill_bitmap.rows
        x_offset = (c_x - c_x_fill) // 2
        y_offset = (c_y - c_y_fill) // 2

        # NOTE: This is EVEN SLOWER than the pervious copy!
        # It should be changed as soon as possible.
        fill_buffer = fill_bitmap.buffer
        for y in range(c_y_fill):
            for x in range(c_x_fill):
                i_src = y * c_x_fill + x
                i_target = (y + y_offset) * c_x + x + x_offset

                buffer[i_target * 2] = fill_buffer[i_src]

        buffer.resize(c_y * 2, c_x * 2, refcheck=False)

        prototype = _CharPrototype(
            char, buffer, c_x, c_y, o_x, o_y, face.glyph.advance.x >> 6)

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

        atlas = np.zeros((atlas_height * 2, atlas_width * 2), dtype=np.uint8)

        offset_x = (0.5 / atlas_width)
        offset_y = (0.5 / atlas_height)

        cur_x = 0
        cur_y = 0
        for char_data in to_combine.values():
            if cur_x + char_data.width * 2 > atlas_width * 2:
                cur_x = 0
                # we use 2 bytes per pixel so offsets have to be
                # multiplied by two as well
                cur_y += rows_heights.pop(0) * 2

            width = char_data.width
            height = char_data.height

            atlas[cur_y:cur_y + height * 2,
                  cur_x:cur_x + width * 2] = char_data.data

            tex_x = ((cur_x / 2) / atlas_width) + offset_x
            tex_y = ((cur_y / 2) / atlas_height) + offset_y
            tex_width = (width / atlas_width) - offset_x
            tex_height = (height / atlas_height) - offset_y

            tex_rect = Rectangle(tex_x, tex_y, tex_width, tex_height)
            glyph_obj = Glyph(glm.ivec2(width, height), glm.ivec2(
                char_data.left, char_data.top), char_data.advance, tex_rect)

            self.glyphs[char_data.char] = glyph_obj

            cur_x += width * 2

        texture_data = TextureData()
        texture_data.width = atlas_width
        texture_data.height = atlas_height
        texture_data.data = atlas

        texture_spec = TextureSpec()
        texture_spec.format = TextureFormat.Rg
        texture_spec.internal_format = SizedInternalFormat.Rg8
        texture_spec.mipmaps = 1
        texture_spec.min_filter = MinFilter.Linear
        texture_spec.mag_filter = MagFilter.Linear
        texture_spec.wrap_mode = WrapMode.ClampToEdge
        texture_spec.pixel_alignment = 2
        texture_spec.texture_swizzle = SwizzleTarget.TextureSwizzleRgba
        # texture_spec.swizzle_mask = [
        #     SwizzleMask.Red, SwizzleMask.Red, SwizzleMask.Red, SwizzleMask.Green]
        texture_spec.swizzle_mask = [
            SwizzleMask.Green, SwizzleMask.Green, SwizzleMask.Green, SwizzleMask.Red]

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
            raise SpykeException(f'Cannot find glyph: "{char}"')

        return self.glyphs[char]
