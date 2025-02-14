import io

import numpy as np
from PIL import Image as PILImage
from pygl import textures

from spyke import debug
from spyke.assets.asset_config import AssetConfig
from spyke.assets.asset_loader import AssetLoader
from spyke.assets.image import ImageConfig, ImageLoadData

_PNG_MAGIC_VALUE = b'\x89PNG\r\n\x1a\n'
_JPG_MAGIC_VALUES = b'\xff\xd8\xff' # i don't know if it's enough to just check those 3 bytes...

class StandardImageLoader(AssetLoader):
    '''
    Loader used to load images from standard files.
    '''

    def can_process_file_data(self, file_data: bytes) -> bool:
        return file_data.startswith((_PNG_MAGIC_VALUE, _JPG_MAGIC_VALUES))

    @debug.profiled
    def load_from_binary(self, data: bytes, config: AssetConfig) -> ImageLoadData:
        assert isinstance(config, ImageConfig), 'Invalid type of config provided to StandardImageLoader'

        fp = io.BytesIO(data)

        with PILImage.open(fp, 'r') as img:
            bits = 8 if img.format == 'PNG' else img.bits # type: ignore
            mode = img.mode
            width = img.width
            height = img.height

            img_data = _load_image_data(img)

        return ImageLoadData(
            textures.TextureSpec(
                textures.TextureTarget.TEXTURE_2D,
                width,
                height,
                _image_mode_to_internal_format(mode, bits),
                mipmaps=config.mipmap_count,
                min_filter=config.min_filter,
                mag_filter=config.mag_filter),
            [textures.UploadInfo(
                _image_mode_to_pixel_format(mode),
                width,
                height)],
            img_data,
            unpack_alignment=1)

@debug.profiled
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

    return data

def _image_mode_to_pixel_format(mode: str) -> textures.PixelFormat:
    match mode.lower():
        case 'rgba':
            return textures.PixelFormat.RGBA
        case 'rgb':
            return textures.PixelFormat.RGB
        case invalid:
            raise ValueError(f'Invalid image mode: {invalid}')

def _image_mode_to_internal_format(mode: str, bits: int) -> textures.InternalFormat:
    mode = mode.lower()

    match mode, bits:
        case 'rgba', 8:
            return textures.InternalFormat.RGBA8
        case 'rgba', 16:
            return textures.InternalFormat.RGBA16
        case 'rgb', 8:
            return textures.InternalFormat.RGB8

    raise ValueError(f'Invalid mode and bits combination: {mode}, {bits}')
