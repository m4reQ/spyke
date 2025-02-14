import ctypes as ct

import numpy as np
from pygl import textures

from spyke import debug
from spyke.assets.asset_config import AssetConfig
from spyke.assets.asset_loader import AssetLoader
from spyke.assets.image import ImageConfig, ImageLoadData

_DDS_MAGIC_VALUE = b'DDS '

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

class DDSLoader(AssetLoader):
    '''
    Loader used to load images from compressed image files.
    '''

    def can_process_file_data(self, file_data: bytes) -> bool:
        return file_data.startswith(_DDS_MAGIC_VALUE)

    @debug.profiled
    def load_from_binary(self, data: bytes, config: AssetConfig):
        assert isinstance(config, ImageConfig), 'Invalid config type provided to DDSLoader'

        # at this point loader should not get invalid magic value
        header = _DDSHeader.from_buffer_copy(data)
        img_data = np.frombuffer(data, dtype=np.ubyte, offset=ct.sizeof(_DDSHeader))
        internal_format, block_size = _determine_internal_format(header.bits_per_pixel, header.fourcc)

        return ImageLoadData(
            textures.TextureSpec(
                textures.TextureTarget.TEXTURE_2D,
                header.width,
                header.height,
                internal_format,
                mipmaps=header.mipmap_count,
                min_filter=config.min_filter,
                mag_filter=config.mag_filter),
            _create_upload_infos(
                header.width,
                header.height,
                header.mipmap_count,
                block_size,
                internal_format),
            img_data,
            unpack_alignment=1)

def _determine_internal_format(bpp: int, fourcc: bytes) -> tuple[textures.CompressedInternalFormat, int]:
    if fourcc == b'DXT1':
        if bpp == 24:
            return (textures.CompressedInternalFormat.COMPRESSED_RGB_S3TC_DXT1_EXT, 8)
        elif bpp == 32:
            return (textures.CompressedInternalFormat.COMPRESSED_RGBA_S3TC_DXT1_EXT, 8)

        raise RuntimeError('Invalid bits per pixel for DXT1 compressed data.')
    elif fourcc == b'DXT3':
        return (textures.CompressedInternalFormat.COMPRESSED_RGBA_S3TC_DXT3_EXT, 16)
    elif fourcc == b'DXT5':
        return (textures.CompressedInternalFormat.COMPRESSED_RGBA_S3TC_DXT5_EXT, 16)

    raise RuntimeError('Loader does not support DDS files with DXT10 format')

@debug.profiled
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
