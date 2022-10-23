import numpy as np
from PIL import Image as PILImage
from spyke import debug
from spyke.graphics.textures import Texture2D, TextureSpec, TextureUploadData
from spyke.resources.types import Image
from spyke.utils import convert

from .image_loading_data import ImageLoadingData
from .loader import LoaderBase


class StandardImageLoader(LoaderBase[Image, ImageLoadingData]):
    '''
    Loader used to load images from standard files.
    '''

    __supported_extensions__ = ['.png', '.jpg', '.jpeg']

    @staticmethod
    @debug.profiled('resources', 'io')
    def load_from_file(filepath: str) -> ImageLoadingData:
        with PILImage.open(filepath, 'r') as img:
            bits: int
            if img.format == 'PNG':
                bits = 8
            else:
                bits = img.bits # type: ignore

            texture_format = convert.image_mode_to_texture_format(img.mode)
            spec = TextureSpec(
                img.width,
                img.height,
                convert.texture_format_to_internal_format(texture_format, bits))
            data = TextureUploadData(
                img.width,
                img.height,
                _load_image_data(img),
                texture_format)

        return ImageLoadingData(spec, [data])

    @staticmethod
    @debug.profiled('resources', 'initialization')
    def finalize_loading(resource: Image, loading_data: ImageLoadingData) -> None:
        texture = Texture2D(loading_data.specification)
        texture.upload(loading_data.upload_data[0])

        with resource.lock:
            resource.texture = texture
            resource.is_loaded = True

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
