import uuid
import typing as t

from spyke.graphics import Glyph
from spyke.graphics.texturing.texture import Texture
from .resource import ResourceBase

class Font(ResourceBase):
    @staticmethod
    def get_suitable_extensions() -> t.List[str]:
        return ['.ttf', '.otf']

    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.texture: Texture
        self.glyphs: t.Dict[str, Glyph] = {}
        self.base_size = 1
        self.name = ''

    def _unload(self) -> None:
        pass

    def get_glyph(self, char: str) -> Glyph:
        if char not in self.glyphs:
            return self.glyphs['\n']

        return self.glyphs[char]
