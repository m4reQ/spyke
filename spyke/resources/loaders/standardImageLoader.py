from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from PIL import Image as _Image
from typing import List, Type
from spyke.enums import _TextureFormat, PixelType
from spyke.graphics.texturing import TextureSpec, Texture
from spyke.resources.types import Image
from spyke.utils import convert
from .loader import Loader, LoadingData

@dataclass
class _TextureData(LoadingData):
    specification: TextureSpec
    texture_format: _TextureFormat
    image_format: str
    pixels: np.ndarray

def _load_image_data(img: _Image.Image) -> np.ndarray:
    img.load()

    encoder = _Image._getencoder(img.mode, 'raw', img.mode)
    encoder.setimage(img.im)

    shape, typestr = _Image._conv_type_shape(img)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        _, s, d = encoder.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)

    assert s >= 0, 'Encoder error.'

    return data


class StandardImageLoader(Loader[_TextureData, Image]):
    '''
    Loader used to load images from standard files.
    '''

    __extensions__: List[str] = ['PNG', 'JPG', 'JPEG']
    __restype__: Type[Image] = Image

    def _load(self) -> None:
        with _Image.open(self.filepath, 'r') as img:
            data = _load_image_data(img)

            if img.format == 'PNG':
                bits = 8
            else:
                bits = img.bits

            texture_format = convert.image_mode_to_texture_format(img.mode)
            internal_format = convert.texture_format_to_internal_format(texture_format, bits)

            spec = TextureSpec()
            spec.width = img.width
            spec.height = img.height
            spec.internal_format = internal_format

            self._data = _TextureData(spec, texture_format, img.format, data)
        
    def finalize(self) -> None:
        if self.had_loading_error:
            with self.resource.lock:
                self.resource.is_invalid = True
                self.resource.texture = Texture.invalid()
            
            return

        texture = Texture(self._data.specification)
        texture.upload(None, 0, self._data.texture_format, PixelType.UnsignedByte, self._data.pixels)
        texture.generate_mipmap()
        texture._check_immutable()

        with self.resource.lock:
            self.resource.texture = texture