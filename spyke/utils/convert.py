from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Any

from spyke.enums import GLType, SizedInternalFormat, TextureFormat
import ctypes
import numpy as np

_GL_TYPE_TO_SIZE_MAP = {
    GLType.Byte: ctypes.sizeof(ctypes.c_byte),
    GLType.UnsignedByte: ctypes.sizeof(ctypes.c_ubyte),
    GLType.Short: ctypes.sizeof(ctypes.c_short),
    GLType.UnsignedShort: ctypes.sizeof(ctypes.c_ushort),
    GLType.Int: ctypes.sizeof(ctypes.c_int),
    GLType.UnsignedInt: ctypes.sizeof(ctypes.c_uint),
    GLType.Float: ctypes.sizeof(ctypes.c_float),
    GLType.Double: ctypes.sizeof(ctypes.c_double),
    GLType.HalfFloat: ctypes.sizeof(ctypes.c_float) // 2,
    GLType.Fixed: ctypes.sizeof(ctypes.c_int)
}

# TODO: Add typing for numpy dtypes
_GL_TYPE_TO_NP_TYPE_MAP = {
    GLType.Byte: np.byte,
    GLType.UnsignedByte: np.ubyte,
    GLType.Short: np.short,
    GLType.UnsignedShort: np.ushort,
    GLType.Int: np.intc,
    GLType.UnsignedInt: np.uintc,
    GLType.Float: np.single,
    GLType.Double: np.double,
    GLType.HalfFloat: np.half,
    GLType.Fixed: np.intc
}

_IMAGE_MODE_TO_TEXTURE_FORMAT_MAP = {
    'rgba': TextureFormat.Rgba,
    'rgb': TextureFormat.Rgb
}

_TEXTURE_FORMAT_TO_INTERNAL_FORMAT_MAP = {
    TextureFormat.Rgba: SizedInternalFormat.Rgba8,
    TextureFormat.Rgb: SizedInternalFormat.Rgb8,
}


def texture_format_to_internal_format(_format: TextureFormat) -> SizedInternalFormat:
    assert _format in _TEXTURE_FORMAT_TO_INTERNAL_FORMAT_MAP, f'Invalid OpenGL texture format: {_format}.'
    return _TEXTURE_FORMAT_TO_INTERNAL_FORMAT_MAP[_format]


def gl_type_to_size(gl_type: GLType) -> int:
    assert gl_type in _GL_TYPE_TO_SIZE_MAP, f'Invalid OpenGL type: {gl_type}.'
    return _GL_TYPE_TO_SIZE_MAP[gl_type]


def gl_type_to_np_type(gl_type: GLType) -> Any:
    assert gl_type in _GL_TYPE_TO_NP_TYPE_MAP, f'Invalid OpenGL type: {gl_type}.'
    return _GL_TYPE_TO_NP_TYPE_MAP[gl_type]


def image_mode_to_texture_format(img_mode: str) -> TextureFormat:
    img_mode = img_mode.lower()
    assert img_mode in _IMAGE_MODE_TO_TEXTURE_FORMAT_MAP, f'Invalid image mode: {img_mode}.'
    return _IMAGE_MODE_TO_TEXTURE_FORMAT_MAP[img_mode]
