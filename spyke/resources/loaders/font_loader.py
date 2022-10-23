import dataclasses
import math
import typing as t

import freetype as ft
import glm
import numpy as np
from spyke import debug, utils
from spyke.enums import (MagFilter, MinFilter, SizedInternalFormat,
                         SwizzleMask, SwizzleTarget, TextureFormat, WrapMode)
from spyke.graphics.glyph import Glyph
from spyke.graphics.rectangle import Rectangle
from spyke.graphics.textures import Texture2D, TextureSpec, TextureUploadData
from spyke.resources.types import Font

from .loader import LoaderBase

# TODO: Unhardcode font size
FONT_SIZE = 96

@dataclasses.dataclass
class _CharPrototype:
    char: str
    data: np.ndarray
    width: int
    height: int
    left: int
    top: int
    advance: int

@dataclasses.dataclass
class _FontData:
    texture_specification: TextureSpec
    texture_upload_data: TextureUploadData
    font_name: str
    glyphs: dict[str, Glyph]
    base_size: int

class FontLoader(LoaderBase[Font, _FontData]):
    __supported_extensions__ = ['.ttf', '.otf']

    @staticmethod
    @debug.profiled('resources', 'io')
    def load_from_file(filepath: str) -> _FontData:
        face = ft.Face(filepath)
        assert face.is_scalable, 'Cannot load non scalable fonts'
        face.set_pixel_sizes(0, FONT_SIZE)

        name = face.family_name.decode('utf-8')

        stroker = ft.Stroker()
        stroker.set(
            FONT_SIZE,
            ft.FT_STROKER_LINECAP_ROUND,
            ft.FT_STROKER_LINEJOIN_ROUND,
            0)

        chars = _get_all_characters(face)
        to_combine = {char: _load_char_data(char, face, stroker) for char in chars}

        cols = max(utils.get_closest_factors(len(chars)))

        atlas_width, atlas_height, rows_heights = _determine_atlas_size(to_combine.values(), cols)

        atlas_width += cols
        atlas_height += len(rows_heights)

        atlas = np.zeros((atlas_height, atlas_width), dtype=np.ubyte)

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
            glyph_obj = Glyph(
                glm.ivec2(width, height),
                glm.ivec2(char_data.left, char_data.top),
                char_data.advance,
                tex_rect)

            glyphs[char_data.char] = glyph_obj

            cur_x += width + 1

        texture_spec = TextureSpec(
            atlas_width,
            atlas_height,
            SizedInternalFormat.R8,
            mipmaps=1,
            min_filter=MinFilter.Linear,
            mag_filter=MagFilter.Linear,
            wrap_mode=WrapMode.ClampToEdge,
            texture_swizzle=SwizzleTarget.TextureSwizzleRgba,
            swizzle_mask=[SwizzleMask.One, SwizzleMask.One, SwizzleMask.One, SwizzleMask.Red])

        upload_data = TextureUploadData(
            atlas_width,
            atlas_height,
            atlas,
            TextureFormat.Red)

        return _FontData(
            texture_spec,
            upload_data,
            name,
            glyphs,
            face.size.x_ppem)

    @staticmethod
    @debug.profiled('resources', 'initialization')
    def finalize_loading(resource: Font, loading_data: _FontData) -> None:
        tex = Texture2D(loading_data.texture_specification)
        Texture2D.set_pixel_unpack_alignment(1)
        tex.upload(loading_data.texture_upload_data)
        Texture2D.set_pixel_unpack_alignment(4)

        with resource.lock:
            resource.texture = tex
            resource.glyphs = loading_data.glyphs
            resource.name = loading_data.font_name
            resource.base_size = loading_data.base_size
            resource.is_loaded = True

def _get_all_characters(face: ft.Face) -> t.List[str]:
    return [chr(idx) for _, idx, in face.get_chars() if chr(idx).isprintable()] + ['\n', ]

def _load_char_data(char: str, face: ft.Face, stroker: ft.Stroker) -> _CharPrototype:
    face.load_char(
        char,
        ft.FT_LOAD_TARGET_NORMAL | ft.FT_LOAD_NO_BITMAP | ft.FT_LOAD_FORCE_AUTOHINT)

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
        char,
        data,
        width_stroke,
        height_stroke,
        origin_x,
        origin_y,
        face.glyph.advance.x >> 6)

    return prototype

def _determine_atlas_size(chars_data: t.Iterable[_CharPrototype], cols: int) -> tuple[int, int, list[int]]:
    atlas_width = 0
    rows_heights: t.List[int] = list()

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
