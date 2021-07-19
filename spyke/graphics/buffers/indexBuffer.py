from ..gl import GLObject, GLHelper
from ...constants import _INT_SIZE, _GL_INDEX_TYPE_NUMPY_TYPE_MAP

from OpenGL import GL
import numpy as np

class IndexBuffer(GLObject):
	_BufferStorageFlags = 0

	@staticmethod
	def CreateQuadIndices(quadsCount: int) -> list:
		data = []

		offset = 0
		i = 0
		while i < quadsCount:
			data.extend([
				0 + offset,
				1 + offset,
				2 + offset,
				2 + offset,
				3 + offset,
				0 + offset])
			
			offset += 4
			i += 1
		
		return data
		
	def __init__(self, data: list, indicesType: GL.GLenum):
		super().__init__()
		self._size = len(data) * _INT_SIZE
		self._type = indicesType
		self._id = GLHelper.CreateBuffer()

		GL.glNamedBufferStorage(self._id, self._size, np.asarray(data, dtype=_GL_INDEX_TYPE_NUMPY_TYPE_MAP[indicesType]), IndexBuffer._BufferStorageFlags)
	
	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteBuffers(1, [self._id])
		
	@property
	def Size(self):
		return self._size
	
	@property
	def Type(self):
		return self._type