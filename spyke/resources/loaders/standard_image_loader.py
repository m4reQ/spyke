import typing as t
from dataclasses import dataclass

import numpy as np
from PIL import Image as PILImage

from spyke.enums import _TextureFormat, PixelType
from spyke.graphics.texturing import TextureSpec, Texture
from spyke.resources.types import Image
from spyke.utils import convert
from spyke import debug
from .loader import LoaderBase

@debug.profiled('resources')
def _load_image_data(img: PILImage.Image) -> np.ndarray:
    img.load()

    encoder = PILImage._getencoder(img.mode, 'raw', img.mode) # type: ignore
    encoder.setimage(img.im)

    shape, typestr = PILImage._conv_type_shape(img) # type: ignore
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        _, s, d = encoder.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)

    assert s >= 0, 'Encoder error.'

    return data

@dataclass
class _TextureData:
    specification: TextureSpec
    texture_format: _TextureFormat
    pixels: np.ndarray

class StandardImageLoader(LoaderBase[Image]):
    '''
    Loader used to load images from standard files.
    '''

    @staticmethod
    def get_suitable_extensions() -> t.List[str]:
        return ['.png', '.jpg', '.jpeg']

    @debug.profiled('resources')
    def load(self, filepath: str) -> t.Any:
        spec = TextureSpec()

        with PILImage.open(filepath, 'r') as img:
            data = _load_image_data(img)

            bits: int
            if img.format == 'PNG':
                bits = 8
            else:
                bits = img.bits # type: ignore

            texture_format = convert.image_mode_to_texture_format(img.mode)

            spec.internal_format = convert.texture_format_to_internal_format(texture_format, bits)
            spec.width = img.width
            spec.height = img.height

        return _TextureData(spec, texture_format, data)

    @debug.profiled('resources')
    def finish_loading(self) -> None:
        data: _TextureData = self.loading_data

        texture = Texture(data.specification)
        texture.upload(
            None,
            0,
            data.texture_format,
            PixelType.UnsignedByte,
            data.pixels)
        texture.generate_mipmap()
        texture.check_immutable()

        self.resource.texture = texture
