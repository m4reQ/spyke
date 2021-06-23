from .aVertexBuffer import AVertexBuffer
from ...constants import _NP_FLOAT, _GL_FLOAT_SIZE

from OpenGL import GL
import numpy as np

class StaticVertexBuffer(AVertexBuffer):
	_BufferUsageFlags = 0

	def __init__(self, data: list):
		super().__init__(len(data) * _GL_FLOAT_SIZE, data, StaticVertexBuffer._BufferUsageFlags)
	
class VertexBuffer(AVertexBuffer):
	_BufferUsageFlags = GL.GL_DYNAMIC_STORAGE_BIT

	def __init__(self, size: int, data=None):
		super().__init__(size, data, VertexBuffer._BufferUsageFlags)
	
	def AddData(self, data: int, size: int) -> None:
		GL.glNamedBufferSubData(self._id, 0, size, np.asarray(data, dtype=_NP_FLOAT))