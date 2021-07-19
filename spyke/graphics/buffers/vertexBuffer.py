from .aBuffer import ABuffer
from ...constants import _NP_FLOAT, _GL_FLOAT_SIZE

from OpenGL import GL
import numpy as np

class StaticVertexBuffer(ABuffer):
	_BufferUsageFlags = 0

	def __init__(self, data: list):
		super().__init__(len(data) * _GL_FLOAT_SIZE)

		GL.glNamedBufferStorage(self._id, self._size, np.asarray(data, dtype=_NP_FLOAT), StaticVertexBuffer._BufferUsageFlags)
	
class VertexBuffer(ABuffer):
	_BufferUsageFlags = GL.GL_DYNAMIC_STORAGE_BIT

	def __init__(self, size: int, dataStorageView: memoryview):
		super().__init__(size)

		self._dataView = dataStorageView

		GL.glNamedBufferStorage(self._id, self._size, None, VertexBuffer._BufferUsageFlags)
	
	def TransferData(self, size: int) -> None:
		"""
		Transfer given amount of data from bound data storage
		to buffer's memory.
		"""

		GL.glNamedBufferSubData(self._id, 0, size, self._dataView.obj)
	
	def __del__(self):
		self._dataView.release()