import ctypes as ct

import numpy as np
from PIL import Image as PILImage

from pygl import textures
from spyke import debug
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
            f.seek(0)

            header = _DDSHeader()
            f.readinto(header)

            assert header.signature == b'DDS ', 'Provided file is not a DDS file'

            fourcc = header.fourcc.decode('utf-8')
            assert fourcc.startswith('DXT'), 'Loader only supports DXT(1|3|5) formats'

            internal_format, block_size = _determine_internal_format(img.mode, fourcc)

            data = np.frombuffer(f.read(), dtype=np.ubyte)

        return ImageLoadingData(
            textures.TextureSpec(
                textures.TextureTarget.TEXTURE_2D,
                header.width,
                header.height,
                internal_format,
                mipmaps=header.mipmap_count),
            _create_upload_infos(
                header.width,
                header.height,
                header.mipmap_count,
                block_size,
                internal_format),
            data)

    @staticmethod
    @debug.profiled('resources', 'initialization')
    def finalize_loading(resource: Image, loading_data: ImageLoadingData) -> None:
        texture = _create_texture(loading_data.specification)
        _upload_texture_data(texture, loading_data.upload_infos, loading_data.upload_data)

        with resource.lock:
            resource.texture = texture
            resource.is_loaded = True

@debug.profiled('resources', 'initialization')
def _upload_texture_data(texture: textures.Texture, infos: list[textures.UploadInfo], data: np.ndarray) -> None:
    for info in infos:
        texture.upload(info, data)

@debug.profiled('resources', 'initialization')
def _create_texture(spec: textures.TextureSpec) -> textures.Texture:
    return textures.Texture(spec)

def _determine_internal_format(img_mode: str, fourcc: str) -> tuple[textures.CompressedInternalFormat, int]:
    texture_format: textures.CompressedInternalFormat
    block_size: int
    match img_mode, fourcc[-1]:
        case 'RGB', '1':
            texture_format = textures.CompressedInternalFormat.COMPRESSED_RGB_S3TC_DXT1_EXT
            block_size = 8
        case 'RGBA', '1':
            texture_format = textures.CompressedInternalFormat.COMPRESSED_RGBA_S3TC_DXT1_EXT
            block_size = 8
        case 'RGBA', '3':
            texture_format = textures.CompressedInternalFormat.COMPRESSED_RGBA_S3TC_DXT3_EXT
            block_size = 16
        case 'RGBA', '5':
            texture_format = textures.CompressedInternalFormat.COMPRESSED_RGBA_S3TC_DXT5_EXT
            block_size = 16
        case _, '0':
            raise RuntimeError('Loader does not support DXT10 format')
        case _:
            raise TypeError(f'Unsupported compressed file format: {fourcc}')

    return (texture_format, block_size)

@debug.profiled('resources', 'initialization')
def _create_upload_infos(width: int,
                        height: int,
                        mipmaps: int,
                        block_size: int,
                        internal_format: textures.CompressedInternalFormat) -> list[textures.UploadInfo]:
    infos = list[textures.UploadInfo]()
    offset = 0
    w = width
    h = height
    for i in range(0, mipmaps):
        if w == 0 or h == 0:
            break

        size = ((w + 3) // 4) * ((h + 3) // 4) * block_size

        info = textures.UploadInfo(
            internal_format,
            w,
            h,
            level=i,
            image_size=size,
            generate_mipmap=False,
            data_offset=offset)

        offset += size
        w //= 2
        h //= 2

        infos.append(info)

    return infos
