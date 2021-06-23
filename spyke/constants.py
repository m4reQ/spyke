import ctypes
import numpy as np
from OpenGL import GL

START_TIME = 0.0

USE_FAST_NV_MULTISAMPLE = False

DEFAULT_LOG_FILENAME = "novaDefaultLog.log"

_OPENGL_VER_MAJOR = 4
_OPENGL_VER_MINOR = 5

_MAIN_PROCESS = None

_GL_FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
_GL_INT_SIZE = ctypes.sizeof(ctypes.c_int)
_FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
_INT_SIZE = ctypes.sizeof(ctypes.c_int)

_NP_BYTE = np.int8
_NP_INT = np.int32
_NP_LONG = np.int64
_NP_FLOAT = np.float32
_NP_DOUBLE = np.float64
_NP_UINT = np.uint32

_GL_INDEX_TYPE_NUMPY_TYPE_MAP = {
	GL.GL_UNSIGNED_BYTE: np.uint8,
	GL.GL_UNSIGNED_SHORT: np.uint16,
	GL.GL_UNSIGNED_INT: np.uint32
}

_GL_TYPE_SIZE_MAP = {
	GL.GL_DOUBLE: 8,
	GL.GL_FIXED: 4,
	GL.GL_FLOAT: 4,
	GL.GL_UNSIGNED_INT: 4,
	GL.GL_INT: 4,
	GL.GL_UNSIGNED_SHORT: 2,
	GL.GL_SHORT: 2,
	GL.GL_HALF_FLOAT: 2,
	GL.GL_UNSIGNED_BYTE: 1,
	GL.GL_BYTE: 1
}

_IMAGE_FORMAT_MAP = {
	"JPEG": GL.GL_RGB,
	"JPG": GL.GL_RGB,
	"PNG": GL.GL_RGBA,
	"RGB": GL.GL_RGB,
	"RGBA": GL.GL_RGBA
}