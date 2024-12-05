import numpy as np
from PIL import Image as PILImage

from pygl import textures
from spyke import debug
from spyke.resources.types import Image

from .image_loading_data import ImageLoadingData
from .loader import LoaderBase

_DEFAULT_MIPMAPS_COUNT = 4

class StandardImageLoader(LoaderBase[Image, ImageLoadingData]):
    '''
    Loader used to load images from standard files.
    '''

    __supported_extensions__ = ['.png', '.jpg', '.jpeg']

    @staticmethod
    @debug.profiled('resources', 'io')
    def load_from_file(filepath: str) -> ImageLoadingData:
        width: int
        height: int
        bits: int
        mode: str
        with PILImage.open(filepath, 'r') as img:
            bits = 8 if img.format == 'PNG' else img.bits # type: ignore
            mode = img.mode
            width = img.width
            height = img.height

            data = _load_image_data(img)

        return ImageLoadingData(
            textures.TextureSpec(
                textures.TextureTarget.TEXTURE_2D,
                width,
                height,
                _image_mode_to_internal_format(mode, bits),
                mipmaps=_DEFAULT_MIPMAPS_COUNT),
            [textures.UploadInfo(
                _image_mode_to_pixel_format(mode),
                width,
                height)],
            data)

    @staticmethod
    @debug.profiled('resources', 'initialization')
    def finalize_loading(resource: Image, loading_data: ImageLoadingData) -> None:
        texture = _create_texture(loading_data.specification)
        _upload_texture_data(texture, loading_data.upload_infos[0], loading_data.upload_data)

        with resource.lock:
            resource.texture = texture
            resource.is_loaded = True

@debug.profiled('resources', 'initialization')
def _upload_texture_data(texture: textures.Texture, info: textures.UploadInfo, data: np.ndarray) -> None:
    texture.upload(info, data)

@debug.profiled('resources', 'initialization')
def _create_texture(spec: textures.TextureSpec) -> textures.Texture:
    return textures.Texture(spec)

@debug.profiled('resources', 'io')
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
    match mode.lower(), bits:
        case 'rgba', 8:
            return textures.InternalFormat.RGBA8
        case 'rgba', 16:
            return textures.InternalFormat.RGBA16
        case 'rgb', 8:
            return textures.InternalFormat.RGB8
        case invalid_mode, invalid_bits:
            raise ValueError(f'Invalid mode and bits combination: {invalid_mode}, {invalid_bits}')
