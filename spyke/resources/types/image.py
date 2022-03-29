from __future__ import annotations
from spyke.graphics import Texture
from ..resource import Resource
from uuid import UUID


class Image(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.texture: Texture

    def _unload(self) -> None:
        self.texture.delete()
