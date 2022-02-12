from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Dict
    from uuid import UUID
    from spyke.graphics import Texture, Glyph

from .resource import Resource


class Font(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture
        self.glyphs: Dict[str, Glyph] = {}
        self.base_size: int = 0
        self.name: str = ''

    def _load(self, *, size: int = 64, **_) -> None:
        self._loading_data = self._loader.load(self.filepath, size)
        self.base_size = size

    def _finalize(self) -> None:
        self.texture, self.glyphs, self.name = self._loader.finalize(
            self._loading_data)

    def _unload(self) -> None:
        self.texture.delete()

    def get_glyph(self, char: str) -> Glyph:
        if char not in self.glyphs:
            return self.glyphs['\n']

        return self.glyphs[char]
