from __future__ import annotations
from spyke.exceptions import GraphicsException
from spyke.enums import MagFilter, MinFilter, PixelType, S3tcCompressedInternalFormat, TextureParameter
from spyke.graphics.texturing import Texture, TextureSpec
from spyke.loaders.textureData import TextureData, CompressedTextureData
from spyke.loaders.loader import Loader, LoadingData
from spyke.utils import convert
from typing import Tuple
from PIL import Image
import numpy as np
import ctypes as ct
import io


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


def _load_image_data(img: Image.Image) -> np.ndarray:
    img.load()

    encoder = Image._getencoder(img.mode, 'raw', img.mode)
    encoder.setimage(img.im)

    shape, typestr = Image._conv_type_shape(img)
    data = np.empty(shape, dtype=np.dtype(typestr))
    mem = data.data.cast('B', (data.data.nbytes,))

    bufsize, s, offset = 65536, 0, 0
    while not s:
        _, s, d = encoder.encode(bufsize)
        mem[offset:offset + len(d)] = d
        offset += len(d)
    if s < 0:
        raise GraphicsException(f'Encoder error.')

    return data


def _finalize_normal_texture(data: TextureData):
    texture = Texture(data.specification)
    texture.upload(None, 0, data.texture_format,
                   PixelType.UnsignedByte, data.pixels)
    texture.generate_mipmap()
    texture._check_immutable()

    return texture


class JPEGLoader(Loader):
    __restypes__ = ['JPEG', 'JPG']

    def load(self, img: Image.Image, *_) -> TextureData:
        data = _load_image_data(img)

        texture_format = convert.image_mode_to_texture_format(img.mode)
        internal_format = convert.texture_format_to_internal_format(
            texture_format, img.bits)

        spec = TextureSpec()
        spec.width = img.width
        spec.height = img.height
        spec.internal_format = internal_format

        return TextureData(spec, texture_format, img.format, data)

    def finalize(self, data: TextureData, *_) -> Texture:
        return _finalize_normal_texture(data)


class PNGLoader(Loader):
    __restypes__ = 'PNG'

    def load(self, img: Image.Image, *_) -> TextureData:
        data = _load_image_data(img)

        texture_format = convert.image_mode_to_texture_format(img.mode)
        internal_format = convert.texture_format_to_internal_format(
            texture_format, 8)

        spec = TextureSpec()
        spec.width = img.width
        spec.height = img.height
        spec.internal_format = internal_format

        return TextureData(spec, texture_format, img.format, data)

    def finalize(self, data: TextureData, *_) -> Texture:
        return _finalize_normal_texture(data)


class DDSLoader(Loader):
    __restypes__ = 'DDS'

    def load(self, img: Image.Image) -> CompressedTextureData:
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
        assert fourcc.startswith(
            'DXT'), 'Loader only supports DXT(1|3|5) formats'

        texture_format, block_size = self._determine_texture_format(
            img.mode, fourcc)

        buffer_size = file_size - ct.sizeof(_DDSHeader)
        buffer = np.empty((buffer_size, ), dtype=np.ubyte)
        read = f.readinto(buffer)

        assert read == buffer_size, 'Number of bytes read does not match the destination buffer size'

        spec = TextureSpec()
        spec.width = width
        spec.height = height
        spec.internal_format = texture_format
        spec.mipmaps = mipmap_count

        return CompressedTextureData(spec, texture_format, img.format, buffer, block_size)

    def finalize(self, data: CompressedTextureData, *_) -> Texture:
        texture = Texture(data.specification)
        texture.set_parameter(TextureParameter.MinFilter,
                              MinFilter.LinearMipmapLinear)
        texture.set_parameter(TextureParameter.MagFilter, MagFilter.Linear)

        offset = 0
        w = data.specification.width
        h = data.specification.height
        mipmaps = data.specification.mipmaps
        for i in range(data.specification.mipmaps):
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

        texture._check_immutable()

        return texture

    def _determine_texture_format(self, img_mode: str, fourcc: str) -> Tuple[S3tcCompressedInternalFormat, int]:
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
