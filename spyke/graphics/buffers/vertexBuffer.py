from .aBuffer import ABuffer, AMappable
from ...constants import _GL_TYPE_NP_TYPE_MAP, _GL_TYPE_SIZE_MAP

from OpenGL import GL
import numpy as np

class StaticBuffer(ABuffer):
	_BufferUsageFlags = 0

	def __init__(self, data: list, dataType: GL.GLenum):
		super().__init__(len(data) * _GL_TYPE_SIZE_MAP[dataType], dataType)

		GL.glNamedBufferStorage(self._id, self._size, np.asarray(data, dtype=_GL_TYPE_NP_TYPE_MAP[dataType]), self._BufferUsageFlags)
	
class Buffer(ABuffer):
	_BufferUsageFlags = GL.GL_DYNAMIC_STORAGE_BIT

	def __init__(self, size: int, dataStorageView: memoryview):
		super().__init__(size, None)

		self._dataView = dataStorageView

		GL.glNamedBufferStorage(self._id, self._size, None, self._BufferUsageFlags)
	
	def TransferData(self, size: int) -> None:
		"""
		Transfer given amount of data from bound data storage
		to buffer's memory.
		"""

		GL.glNamedBufferSubData(self._id, 0, size, self._dataView.obj)
	
	def __del__(self):
		self._dataView.release()

class MappedBuffer(AMappable):
	def __init__(self, size: int):
		super().__init__(size, None)

		GL.glNamedBufferStorage(self._id, self._size, None, self._BufferUsageFlags)
		
		self._MapPersistent()