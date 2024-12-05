import uuid

from pygl import textures

from .resource import ResourceBase


class Image(ResourceBase):
    __supported_extensions__ = ['.jpg', '.jpeg', '.png', '.dds']

    empty: uuid.UUID

    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.texture: textures.Texture

    def _unload(self) -> None:
        self.texture.delete()
