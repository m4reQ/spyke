from spyke import utils
from spyke.enums import MagFilter, MinFilter, PixelType, SizedInternalFormat, SwizzleMask, SwizzleTarget, TextureFormat, WrapMode
from spyke.graphics import Glyph, Rectangle, TextureSpec, Texture
from spyke.loaders.fontData import FontData
from spyke.loaders.loader import Loader
from spyke.loaders.textureData import TextureData
from typing import Dict, List, Sequence, Tuple
from dataclasses import dataclass
import math
import glm
import numpy as np
import freetype as ft


@dataclass
class _CharPrototype:
    char: str
    data: np.ndarray
    width: int
    height: int
    left: int
    top: int
    advance: int


class FontLoader(Loader):
    __restypes__ = 'TTF'

    def load(self, filepath: str, font_size: int) -> TextureData:
        face = ft.Face(filepath)
        assert face.is_scalable, 'Cannot load non scalable fonts'
        face.set_pixel_sizes(0, font_size)

        name = face.family_name.decode('utf-8')

        stroker = ft.Stroker()
        stroker.set(font_size, ft.FT_STROKER_LINECAP_ROUND,
                    ft.FT_STROKER_LINEJOIN_ROUND, 0)

        chars = self._get_all_characters(face)
        to_combine = {}
        for char in chars:
            to_combine[char] = self._load_char_data(char, face, stroker)

        cols = max(utils.get_closest_factors(len(chars)))

        atlas_width, atlas_height, rows_heights = self._determine_atlas_size(
            to_combine.values(), cols)

        atlas_width += cols
        atlas_height += len(rows_heights)

        atlas = np.zeros(
            (atlas_height, atlas_width), dtype=np.ubyte)

        glyphs = {}

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

            glyphs[char_data.char] = glyph_obj

            cur_x += width + 1

        texture_spec = TextureSpec()
        texture_spec.width = atlas_width
        texture_spec.height = atlas_height
        texture_spec.internal_format = SizedInternalFormat.R8
        texture_spec.mipmaps = 1
        texture_spec.min_filter = MinFilter.Linear
        texture_spec.mag_filter = MagFilter.Linear
        texture_spec.wrap_mode = WrapMode.ClampToEdge
        texture_spec.texture_swizzle = SwizzleTarget.TextureSwizzleRgba
        texture_spec.swizzle_mask = [
            SwizzleMask.One, SwizzleMask.One, SwizzleMask.One, SwizzleMask.Red]

        texture_data = TextureData(texture_spec, TextureFormat.Red, '', atlas)

        return FontData(texture_data, name, glyphs)

    def finalize(self, data: FontData) -> Tuple[Texture, Dict[str, Glyph], str]:
        texture_data = data.texture_data

        texture = Texture(texture_data.specification)
        Texture.set_pixel_alignment(1)
        texture.upload(None, 0, texture_data.texture_format,
                       PixelType.UnsignedByte, texture_data.pixels)
        Texture.set_pixel_alignment(4)

        texture._check_immutable()

        return (texture, data.glyphs, data.font_name)

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