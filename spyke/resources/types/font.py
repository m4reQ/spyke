import typing as t
import uuid

from pygl import textures
from spyke.graphics.glyph import Glyph

from .resource import ResourceBase


class Font(ResourceBase):
    __supported_extensions__ = ['.ttf', '.otf']

    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.texture: textures.Texture
        self.glyphs: t.Dict[str, Glyph] = {}
        self.base_size = 1
        self.name = ''

    def _unload(self) -> None:
        pass

    def get_glyph(self, char: str) -> Glyph:
        if char not in self.glyphs:
            return self.glyphs['\n']

        return self.glyphs[char]
