from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Dict
    from uuid import UUID
    from spyke.graphics import Texture, Glyph

from .resource import Resource
from spyke import loaders


class Font(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture
        self.glyphs: Dict[str, Glyph] = {}
        self.base_size: int = 0
        self.name: str = ''

    def _load(self, *, size: int = 64, **_) -> None:
        loader = loaders.get('TTF')
        self._loading_data = loader.load(self.filepath, size)
        self.base_size = size

    def _finalize(self) -> None:
        loader = loaders.get('TTF')
        self.texture, self.glyphs, self.name = loader.finalize(
            self._loading_data)

    def _unload(self) -> None:
        self.texture.delete()

    def get_glyph(self, char: str) -> Glyph:
        if char not in self.glyphs:
            return self.glyphs['\n']

        return self.glyphs[char]
