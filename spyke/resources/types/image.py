import typing as t
import uuid

import numpy as np
from spyke.enums import (MagFilter, MinFilter, PixelType, SizedInternalFormat,
                         TextureFormat)
from spyke.graphics.textures import Texture2D, TextureSpec, TextureUploadData

from .resource import ResourceBase


class Image(ResourceBase):
    __supported_extensions__ = ['.jpg', '.jpeg', '.png', '.dds']

    empty: uuid.UUID

    @classmethod
    def create_empty_image(cls):
        img = cls(uuid.uuid4(), '')
        img.is_internal = True

        spec = TextureSpec(
            1,
            1,
            SizedInternalFormat.Rgba8,
            mipmaps=1,
            min_filter=MinFilter.Nearest,
            mag_filter=MagFilter.Nearest)
        tex = Texture2D(spec)
        data = TextureUploadData(
            1,
            1,
            np.array([255, 255, 255, 255], dtype=np.ubyte),
            TextureFormat.Rgba)
        tex.upload(data)

        img.texture = tex
        img.is_loaded = True

        return img

    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.texture: Texture2D

    def _unload(self) -> None:
        self.texture.delete()
