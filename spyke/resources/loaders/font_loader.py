import dataclasses
import math
import typing as t

import freetype as ft
import glm
import numpy as np

from spyke import debug, utils
from spyke.enums import (MagFilter, MinFilter, SizedInternalFormat,
                         TextureFormat, WrapMode)
from spyke.graphics.glyph import Glyph
from spyke.graphics.textures import Texture2D, TextureSpec, TextureUploadData
from spyke.resources.types import Font

from .loader import LoaderBase

# TODO: Unhardcode font size
FONT_SIZE = 96
ATLAS_CHAR_SPACING = 1

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

        protos = [_load_char_data(char, face, stroker) for char in _get_all_characters(face)]
        atlas_width, atlas_height, rows = _determine_atlas_size(protos)
        row_height = atlas_height // rows

        glyphs: dict[str, Glyph] = {}
        atlas = np.zeros((atlas_height, atlas_width), dtype=np.uint8)

        cur_x = 0
        cur_y = 0
        for char_data in protos:
            width = char_data.width
            height = char_data.height

            if cur_x + width > atlas_width:
                cur_x = 0
                cur_y += row_height

            atlas[cur_y:cur_y + height,
                  cur_x:cur_x + width] = char_data.data

            tex_x = cur_x / atlas_width
            tex_y = cur_y / atlas_height
            tex_width = width / atlas_width
            tex_height = height / atlas_height

            tex_coords = np.array(
                [tex_x, tex_y + tex_height,
                tex_x + tex_width, tex_y + tex_height,
                tex_x + tex_width, tex_y,
                tex_x + tex_width, tex_y,
                tex_x, tex_y,
                tex_x, tex_y + tex_height],
                dtype=np.float32)
            glyph_obj = Glyph(
                glm.ivec2(width, height),
                glm.ivec2(char_data.left, char_data.top),
                char_data.advance,
                tex_coords)

            glyphs[char_data.char] = glyph_obj

            cur_x += width + 1

        texture_spec = TextureSpec(
            atlas_width,
            atlas_height,
            SizedInternalFormat.R8,
            mipmaps=1,
            min_filter=MinFilter.Linear,
            mag_filter=MagFilter.Linear,
            wrap_mode=WrapMode.ClampToEdge)

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

def _determine_atlas_size(glyphs: list[_CharPrototype]) -> tuple[int, int, int]:
    rows, cols = utils.get_closest_factors(len(glyphs))

    atlas_height = sum(x.height for x in sorted(glyphs, key=lambda e: e.height, reverse=True)[:rows]) + rows * ATLAS_CHAR_SPACING
    atlas_width = max(sum(glyph.width for glyph in glyphs[i * cols:i * cols + cols]) for i in range(rows)) + cols * ATLAS_CHAR_SPACING

    return atlas_width, atlas_height, rows

def _get_all_characters(face: ft.Face) -> t.List[str]:
    return [chr(idx) for _, idx, in face.get_chars() if chr(idx).isprintable()] + ['\n', ]

def _load_char_data(char: str, face: ft.Face, stroker: ft.Stroker) -> _CharPrototype:
    face.load_char(
        char,
        ft.FT_LOAD_TARGET_NORMAL | ft.FT_LOAD_NO_BITMAP | ft.FT_LOAD_FORCE_AUTOHINT)

    stroke_glyph = face.glyph.get_glyph()
    stroke_glyph.stroke(stroker, True)
    stroke_glyph_r = stroke_glyph.to_bitmap(
        ft.FT_RENDER_MODE_NORMAL,
        0,
        True)
    stroke_bitmap = stroke_glyph_r.bitmap

    stroker.rewind()

    width_stroke = stroke_bitmap.width
    height_stroke = stroke_bitmap.rows

    data = np.array(stroke_bitmap.buffer, dtype=np.uint8, copy=True).reshape(
        height_stroke, width_stroke)

    fill_glyph = face.glyph.get_glyph()
    fill_glyph_r = fill_glyph.to_bitmap(ft.FT_RENDER_MODE_NORMAL, 0, True)
    fill_bitmap = fill_glyph_r.bitmap

    width_fill = fill_bitmap.width
    height_fill = fill_bitmap.rows

    start_x = math.floor((width_stroke - width_fill) / 2)
    start_y = math.floor((height_stroke - height_fill) / 2)

    data_fill = np.array(fill_bitmap.buffer, dtype=np.uint8, copy=True).reshape(
        height_fill,
        width_fill)

    _max_on_region(data, data_fill, (start_x, start_y))

    prototype = _CharPrototype(
        char,
        data,
        width_stroke,
        height_stroke,
        stroke_glyph_r.left,
        stroke_glyph_r.top,
        face.glyph.advance.x >> 6)

    return prototype

def _max_on_region(dst: np.ndarray, src: np.ndarray, start: t.Sequence[int]) -> None:
    '''
    Performs `numpy.maximum` between src array and the part of dst array given by src's
    shape and start position. This function changes the dst array.
    '''

    slices = tuple(slice(x, x + src.shape[i]) for i, x in enumerate(start))
    dst[slices] = np.maximum(dst[slices], src)
