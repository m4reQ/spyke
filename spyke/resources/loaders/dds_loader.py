import io
import typing as t
import ctypes as ct
from dataclasses import dataclass

import numpy as np
from PIL import Image as PILImage

from .loader import LoaderBase
from spyke.resources.types import Image
from spyke.graphics import TextureSpec, Texture
from spyke.enums import (
    _TextureFormat,
    TextureParameter,
    MinFilter,
    MagFilter,
    S3tcCompressedInternalFormat)

@dataclass
class _CompressedTextureData:
    specification: TextureSpec
    texture_format: _TextureFormat
    pixels: np.ndarray
    block_size: int

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
        ('reserved2', ct.c_uint * 3),
    ]


def _determine_texture_format(img_mode: str, fourcc: str) -> t.Tuple[S3tcCompressedInternalFormat, int]:
    if fourcc.endswith('1') and img_mode == 'RGB':
        texture_format = S3tcCompressedInternalFormat.CompressedRgbS3tcDxt1
        block_size = 8
    elif fourcc.endswith('1') and img_mode == 'RGBA':
        texture_format = S3tcCompressedInternalFormat.CompressedRgbaS3tcDxt1
        block_size = 8
    elif fourcc.endswith('3'):
        texture_format = S3tcCompressedInternalFormat.CompressedRgbaS3tcDxt3
        block_size = 16
    elif fourcc.endswith('5'):
        texture_format = S3tcCompressedInternalFormat.CompressedRgbaS3tcDxt5
        block_size = 16
    elif fourcc.endswith('0'):
        raise RuntimeError('Loader does not support DXT10 format')
    else:
        raise RuntimeError(
            f'Unsupported compressed file format: {fourcc}')

    return (texture_format, block_size)

class DDSLoader(LoaderBase[Image]):
    '''
    Loader used to load images from compressed image files.
    '''

    @staticmethod
    def get_suitable_extensions() -> t.List[str]:
        return ['.dds']

    def load(self, filepath: str) -> t.Any:
        with PILImage.open(filepath, 'r') as img:
            f = img.fp # type: ignore
            f.seek(0, io.SEEK_END)
            file_size = f.tell()
            f.seek(0, io.SEEK_SET)

            header = _DDSHeader()
            f.readinto(header)

            assert header.signature == b'DDS ', 'Provided file is not a DDS file'

            width = header.width
            height = header.height
            mipmap_count = header.mipmap_count
            fourcc = header.fourcc.decode('utf-8')
            assert fourcc.startswith('DXT'), 'Loader only supports DXT(1|3|5) formats'

            texture_format, block_size = _determine_texture_format(img.mode, fourcc)

            buffer_size = file_size - ct.sizeof(_DDSHeader)
            buffer = np.empty((buffer_size, ), dtype=np.ubyte)
            read = f.readinto(buffer)

            assert read == buffer_size, 'Number of bytes read does not match the destination buffer size'

        spec = TextureSpec()
        spec.width = width
        spec.height = height
        spec.internal_format = texture_format
        spec.mipmaps = mipmap_count

        return _CompressedTextureData(spec, texture_format, buffer, block_size)
    
    def finish_loading(self) -> None:
        data: _CompressedTextureData = self.loading_data
        specification = data.specification

        texture = Texture(specification)
        texture.set_parameter(TextureParameter.MinFilter, MinFilter.LinearMipmapLinear)
        texture.set_parameter(TextureParameter.MagFilter, MagFilter.Linear)

        offset = 0
        w = specification.width
        h = specification.height
        mipmaps = specification.mipmaps
        for i in range(specification.mipmaps):
            if w == 0 or h == 0:
                mipmaps -= 1
                continue

            size = ((w + 3) // 4) * ((h + 3) // 4) * data.block_size

            texture.upload_compressed(
                (w, h), i, data.texture_format, size, data.pixels[offset:offset + size])

            offset += size
            w //= 2
            h //= 2

        texture.set_parameter(TextureParameter.MaxLevel, mipmaps - 1)
        texture.check_immutable()

        self.resource.texture = texture
