from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Dict
    from uuid import UUID

from PIL import Image
import time
from os import path
from .resource import Resource
from spyke.enums import MagFilter, MinFilter, WrapMode
from spyke.exceptions import SpykeException
from spyke.graphics.texturing import TextureData, TextureSpec, Texture
from spyke.graphics.rectangle import Rectangle
from spyke.utils import loaders, convert
from spyke.graphics import Glyph
from spyke import debug


class Font(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture
        self.glyphs: Dict[str, Glyph] = {}
        self.base_size: int = 0
        self.name: str = ''

    def _parse_line_as_dict(self, line) -> Dict[str, str]:
        data = line.replace('\n', '').split(' ')
        data = [x for x in data if x]

        values = {}
        for x in data:
            key, value = x.split('=')
            values[key] = value

        return values

    def _parse_line(self, line: str) -> Glyph:
        _values = self._parse_line_as_dict(line.replace('char', ''))

        values = {}
        for key, value in _values.items():
            values[key] = int(value)

        tex_rect = Rectangle(values['x'], values['y'],
                             values['width'], values['height'])

        return Glyph(values['width'], values['height'], values['xoffset'], values['yoffset'], values['xadvance'], tex_rect, chr(values['id']))

    def _load(self, *args, **kwargs) -> None:
        image_filepath, _ = path.splitext(self.filepath)
        image_filepath += '.png'

        with Image.open(image_filepath) as img:
            data = loaders.get_image_data(img)
            size = img.size

        texture_data = TextureData(*size)
        texture_data.format = convert.image_mode_to_texture_format(img.mode)
        texture_data.data = data

        texture_spec = TextureSpec()
        texture_spec.compress = False
        texture_spec.mipmaps = 1
        texture_spec.min_filter = MinFilter.Nearest
        texture_spec.mag_filter = MagFilter.Nearest
        texture_spec.wrap_mode = WrapMode.Repeat

        self._loading_data['texture_spec'] = texture_spec
        self._loading_data['texture_data'] = texture_data

        with open(self.filepath, 'r') as f:
            line: str
            for line in f.readlines():
                if line.startswith('info'):
                    values = self._parse_line_as_dict(
                        line.removeprefix('info '))
                    self.base_size = int(values['size'])
                    self.name = values['face'].replace('"', '')
                    continue

                if line.startswith('char '):
                    glyph = self._parse_line(line)
                    self.glyphs[glyph.char] = glyph

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
