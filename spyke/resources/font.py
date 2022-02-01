from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, List
    from uuid import UUID

from PIL import Image
import time
import numpy as np
from os import path
import freetype
from .resource import Resource
from spyke.enums import SizedInternalFormat, MagFilter, MinFilter, SwizzleMask, SwizzleTarget, WrapMode, TextureFormat
from spyke.exceptions import SpykeException
from spyke.graphics.texturing import TextureData, TextureSpec, Texture
from spyke.graphics.rectangle import Rectangle
from spyke.utils import loaders, convert
from spyke.graphics import Glyph
from spyke import debug, utils
import glm


class Font(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture
        self.glyphs: Dict[str, Glyph] = {}
        self.base_size: int = 0
        self.name: str = ''

    def _get_characters(self, face: freetype.Face) -> List[str]:
        return [chr(idx) for _, idx, in face.get_chars() if chr(idx).isprintable()] + ['\n', ]

    def _load(self, *, size: int = 64, **_) -> None:
        self.base_size = size

        face = freetype.Face(self.filepath)
        face.set_pixel_sizes(0, self.base_size)

        chars = self._get_characters(face)

        max_columns, max_rows = utils.get_closest_factors(len(chars))

        atlas_width = 0
        atlas_height = max_columns * self.base_size
        current_width = 0
        current_char_idx = 0
        for char in chars:
            if current_char_idx >= max_rows:
                atlas_width = max(atlas_width, current_width)
                current_width = 0
                current_char_idx = 0

            face.load_char(char, freetype.FT_LOAD_RENDER |
                           freetype.FT_LOAD_FORCE_AUTOHINT)

            glyph = face.glyph
            bitmap = glyph.bitmap

            current_width += bitmap.width
            current_char_idx += 1

        atlas = np.zeros((atlas_height, atlas_width), dtype=np.ubyte)

        last_x = 0
        last_y = atlas_height - self.base_size
        for char in chars:
            face.load_char(char, freetype.FT_LOAD_RENDER |
                           freetype.FT_LOAD_FORCE_AUTOHINT)

            glyph = face.glyph
            bitmap = glyph.bitmap

            width = bitmap.width
            height = bitmap.rows

            data = np.asarray(bitmap.buffer, dtype=np.ubyte).reshape(
                (height, width))

            if last_x + width > atlas_width:
                last_y -= self.base_size
                last_x = 0

            atlas[last_y:last_y + height, last_x:last_x + width] = data

            tex_x = (last_x / atlas_width) + (0.5 / atlas_width)
            tex_y = 0.5 / atlas_height
            tex_width = (width / atlas_width) - (0.5 / atlas_width)
            tex_height = (height / atlas_height) - (0.5 / atlas_height)

            tex_rect = Rectangle(tex_x, tex_y, tex_width, tex_height)
            glyph_obj = Glyph(glm.ivec2(width, height), glm.ivec2(
                glyph.bitmap_left, glyph.bitmap_top), glyph.advance.x >> 6, tex_rect)
            self.glyphs[char] = glyph_obj

            last_x += width

        texture_data = TextureData()
        texture_data.width = atlas_width
        texture_data.height = atlas_height
        texture_data.data = atlas

        texture_spec = TextureSpec()
        texture_spec.format = TextureFormat.Red
        texture_spec.internal_format = SizedInternalFormat.R8
        texture_spec.mipmaps = 1
        texture_spec.min_filter = MinFilter.Nearest
        texture_spec.mag_filter = MagFilter.Nearest
        texture_spec.wrap_mode = WrapMode.ClampToEdge
        texture_spec.texture_swizzle = SwizzleTarget.TextureSwizzleRgba
        texture_spec.swizzle_mask = [
            SwizzleMask.One, SwizzleMask.One, SwizzleMask.One, SwizzleMask.Red]

        self._loading_data['texture_spec'] = texture_spec
        self._loading_data['texture_data'] = texture_data

    def _finalize(self) -> None:
        self.texture = Texture(
            self._loading_data['texture_data'], self._loading_data['texture_spec'])

        debug.log_info(
            f'Image from file "{self.filepath}" loaded in {time.perf_counter() - self._loading_start} seconds.')

    def _unload(self) -> None:
        self.texture.delete()

    def get_glyph(self, char: str) -> Glyph:
        if char not in self.glyphs:
            raise SpykeException(f'Cannot find glyph: "{char}"')

        return self.glyphs[char]
