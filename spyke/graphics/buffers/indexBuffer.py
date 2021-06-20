from ..gl import GLObject, GLHelper
from ...constants import _INT_SIZE, _NP_INT

from OpenGL import GL
import numpy as np

class IndexBuffer(GLObject):
	@staticmethod
	def CreateQuadIndices(count: int) -> list:
		data = []

		offset = 0
		i = 0
		while i < count:
			data.extend([
				0 + offset,
				1 + offset,
				2 + offset,
				2 + offset,
				3 + offset,
				0 + offset])
			
			offset += 4
			i += 6
		
		return data
		
	def __init__(self, data: list):
		super().__init__()
		self.__size = len(data) * _INT_SIZE
		self._id = GLHelper.CreateBuffer()
		
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._id)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.__size, np.asarray(data, dtype=_NP_INT), GL.GL_STATIC_DRAW)
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
	
	def Bind(self) -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._id)
	
	def Unbind(self) -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
	
	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteBuffers(1, [self._id])
		
	@property
	def Size(self):
		return self.__size