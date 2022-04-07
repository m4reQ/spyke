from __future__ import annotations
from .loader import Loader, LoadingData
from spyke.resources.types import Image
from spyke.enums import _TextureFormat, TextureParameter, MinFilter, MagFilter, S3tcCompressedInternalFormat
from spyke.graphics.texturing import TextureSpec, Texture
from PIL import Image as _Image
from dataclasses import dataclass
from typing import List, Tuple, Type
import ctypes as ct
import io
import numpy as np

@dataclass
class _CompressedTextureData(LoadingData):
    specification: TextureSpec
    texture_format: _TextureFormat
    image_format: str
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


def _determine_texture_format(img_mode: str, fourcc: str) -> Tuple[S3tcCompressedInternalFormat, int]:
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


class DDSLoader(Loader[_CompressedTextureData, Image]):
    '''
    Loader used to load images from compressed image files.
    '''

    __extensions__: List[str] = ['DDS',]
    __restype__: Type[Image] = Image

    def _load(self) -> None:
        with _Image.open(self.filepath, 'r') as img:
            f = img.fp
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

        self._data = _CompressedTextureData(spec, texture_format, img.format, buffer, block_size)

    def finalize(self) -> None:
        if self.had_loading_error:
            with self.resource.lock:
                self.resource.is_invalid = True
                self.resource.texture = Texture.invalid()
            
            return

        specification = self._data.specification
        
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

            size = ((w + 3) // 4) * ((h + 3) // 4) * self._data.block_size

            texture.upload_compressed(
                (w, h), i, self._data.texture_format, size, self._data.pixels[offset:offset + size])

            offset += size
            w //= 2
            h //= 2

        texture.set_parameter(TextureParameter.MaxLevel, mipmaps - 1)
        texture._check_immutable()

        with self.resource.lock:
            self.resource.texture = texture