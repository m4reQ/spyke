from ..gl import GLObject, GLHelper
from ...constants import _NP_FLOAT

from OpenGL import GL
import numpy as np

class VertexBuffer(GLObject):
	def __init__(self, size: int, usage = GL.GL_STREAM_DRAW):
		super().__init__()
		self.__size = size
		self._id = GLHelper.CreateBuffer()

		GL.glNamedBufferData(self._id, self.__size, None, usage)

	def Bind(self) -> None:
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._id)
	
	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteBuffers(1, [self._id])

	def AddData(self, data: list, size: int) -> None:
		GL.glNamedBufferSubData(self._id, 0, size, np.asarray(data, dtype=_NP_FLOAT))
	
	@property
	def Size(self):
		return self.__size