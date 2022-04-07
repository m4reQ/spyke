from __future__ import annotations
from .resource import Resource
from spyke.graphics import Texture, Glyph
from typing import Dict
from uuid import UUID


class Font(Resource):
    def __init__(self, _id: UUID, filepath: str=''):
        super().__init__(_id, filepath)

        self.texture: Texture = Texture.empty()
        self.glyphs: Dict[str, Glyph] = dict()
        self.base_size: int = 0
        self.name: str = ''

    def _unload(self) -> None:
        self.texture.delete()

    def get_glyph(self, char: str) -> Glyph:
        if char not in self.glyphs:
            return self.glyphs['\n']

        return self.glyphs[char]
