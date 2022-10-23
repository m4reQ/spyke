import ctypes as ct

import numpy as np
from PIL import Image as PILImage
from spyke import debug
from spyke.enums import S3tcCompressedInternalFormat
from spyke.graphics.textures import Texture2D, TextureSpec, TextureUploadData
from spyke.resources.types import Image

from .image_loading_data import ImageLoadingData
from .loader import LoaderBase


class _DDSHeader(ct.Structure):
    _fields_ = [
        ('signature', ct.c_char * 4),
        ('unused1', ct.c_uint),
        ('header_content_flags', ct.c_uint),
        ('height', ct.c_uint),
        ('width', ct.c_uint),
        ('pitch', ct.c_uint),
        ('depth', ct.c_uint),
        ('mipmap_count', ct.c_uint),
        ('reserved1', ct.c_uint * 11),
        ('unused2', ct.c_uint),
        ('pixel_info_flags', ct.c_uint),
        ('fourcc', ct.c_char * 4),
        ('bits_per_pixel', ct.c_uint),
        ('red_mask', ct.c_uint),
        ('green_mask', ct.c_uint),
        ('blue_mask', ct.c_uint),
        ('alpha_mask', ct.c_uint),
        ('caps1', ct.c_uint),
        ('caps2', ct.c_uint),
        ('reserved2', ct.c_uint * 3)]

class DDSLoader(LoaderBase[Image, ImageLoadingData]):
    '''
    Loader used to load images from compressed image files.
    '''

    __supported_extensions__ = ['.dds']

    @staticmethod
    @debug.profiled('resources', 'io')
    def load_from_file(filepath: str) -> ImageLoadingData:
        with PILImage.open(filepath, 'r') as img:
            f = img.fp # type: ignore

            header = _DDSHeader()
            f.readinto(header)

            assert header.signature == b'DDS ', 'Provided file is not a DDS file'

            fourcc = header.fourcc.decode('utf-8')
            assert fourcc.startswith('DXT'), 'Loader only supports DXT(1|3|5) formats'

            internal_format, block_size = _determine_internal_format(img.mode, fourcc)

            buf = np.frombuffer(f.read(), dtype=np.ubyte)

        # TODO: Fix inheritance being fucked up in enums related to texture internal format

        spec = TextureSpec(
            header.width,
            header.height,
            internal_format, # type: ignore
            mipmaps=header.mipmap_count)

        upload_data = _create_upload_data(
            header.width,
            header.height,
            header.mipmap_count,
            block_size,
            buf,
            internal_format)

        return ImageLoadingData(spec, upload_data)

    @staticmethod
    @debug.profiled('resources', 'initialization')
    def finalize_loading(resource: Image, loading_data: ImageLoadingData) -> None:
        tex = Texture2D(loading_data.specification)
        for data in loading_data.upload_data:
            tex.upload_compressed(data, False)

        with resource.lock:
            resource.texture = tex
            resource.is_loaded = True

def _determine_internal_format(img_mode: str, fourcc: str) -> tuple[S3tcCompressedInternalFormat, int]:
    texture_format: S3tcCompressedInternalFormat
    block_size: int
    match img_mode, fourcc[-1]:
        case 'RGB', '1':
            texture_format = S3tcCompressedInternalFormat.CompressedRgbS3tcDxt1
            block_size = 8
        case 'RGBA', '1':
            texture_format = S3tcCompressedInternalFormat.CompressedRgbaS3tcDxt1
            block_size = 8
        case 'RGBA', '3':
            texture_format = S3tcCompressedInternalFormat.CompressedRgbaS3tcDxt3
            block_size = 16
        case 'RGBA', '5':
            texture_format = S3tcCompressedInternalFormat.CompressedRgbaS3tcDxt5
            block_size = 16
        case _, '0':
            raise RuntimeError('Loader does not support DXT10 format')
        case _:
            raise TypeError(f'Unsupported compressed file format: {fourcc}')

    return (texture_format, block_size)

def _create_upload_data(width: int,
                        height: int,
                        mipmaps: int,
                        block_size: int,
                        buffer: np.ndarray,
                        internal_format: S3tcCompressedInternalFormat) -> list[TextureUploadData]:
    data: list[TextureUploadData] = []
    offset = 0
    w = width
    h = height
    for i in range(mipmaps - 1, -1, -1):
        if w == 0 or h == 0:
            break

        size = ((w + 3) // 4) * ((h + 3) // 4) * block_size

        _data = TextureUploadData(
            w,
            h,
            buffer[offset:offset + size],
            internal_format, # type: ignore
            i,
            image_size=size)

        offset += size
        w //= 2
        h //= 2

        data.append(_data)

    return data
