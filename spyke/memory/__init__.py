from .glMarshal import GLMarshal
from .serializable import Serializable

from OpenGL import GL
import ctypes

__GL_TYPE_SIZES = {
	GL.GL_DOUBLE: 8,
	GL.GL_FIXED: 4,
	GL.GL_FLOAT: 4,
	GL.GL_UNSIGNED_INT: 4,
	GL.GL_INT: 4,
	GL.GL_UNSIGNED_SHORT: 2,
	GL.GL_SHORT: 2,
	GL.GL_HALF_FLOAT: 2,
	GL.GL_UNSIGNED_BYTE: 1,
	GL.GL_BYTE: 1}

def GetGLTypeSize(_type: int) -> int:
	try:
		return __GL_TYPE_SIZES[_type]
	except KeyError:
		raise RuntimeError(f"Invalid enum: {_type}")

def GetPointer(value: int) -> ctypes.c_void_p:
	return ctypes.c_void_p(value)