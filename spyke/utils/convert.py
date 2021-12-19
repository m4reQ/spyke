from spyke.enums import GLType
from spyke.exceptions import GraphicsException
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

def gl_type_to_size(gl_type: GLType) -> int:
    if __debug__:
        if gl_type not in _GL_TYPE_TO_SIZE_MAP:
            raise GraphicsException(f'Invalid OpenGL type: {gl_type}.')
    
    return _GL_TYPE_TO_SIZE_MAP[gl_type]

def gl_type_to_np_type(gl_type: GLType) -> int:
    if __debug__:
        if gl_type not in _GL_TYPE_TO_NP_TYPE_MAP:
            raise GraphicsException(f'Invalid OpenGL type: {gl_type}.')
    
    return _GL_TYPE_TO_NP_TYPE_MAP[gl_type]
