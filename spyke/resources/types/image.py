import uuid
import typing as t

import numpy as np

from spyke.enums import MagFilter, MinFilter
from spyke.enums.graphics import PixelType, SizedInternalFormat, TextureFormat
from spyke.graphics import Texture, TextureSpec
from .resource import ResourceBase

class Image(ResourceBase):
    empty: uuid.UUID
    
    @staticmethod
    def get_suitable_extensions() -> t.List[str]:
        return ['.jpg', '.jpeg', '.png', '.dds']
    
    @classmethod
    def create_empty_image(cls):
        img = cls(uuid.uuid4(), '')
        img.is_internal = True
        
        spec = TextureSpec(
            width=1,
            height=1,
            mipmaps=1,
            min_filter=MinFilter.Nearest,
            mag_filter=MagFilter.Nearest,
            internal_format=SizedInternalFormat.Rgba8)
        tex = Texture(spec)
        tex.upload(
            None,
            0,
            TextureFormat.Rgba,
            PixelType.UnsignedByte,
            np.array([
                255, 255, 255, 255
            ], dtype=np.ubyte))
        tex.generate_mipmap()
        tex.check_immutable()
        
        img.texture = tex
        
        return img

    def __init__(self, _id: uuid.UUID, filepath: str):
        super().__init__(_id, filepath)

        self.texture = Texture.empty()

    def _unload(self) -> None:
        self.texture.delete()
