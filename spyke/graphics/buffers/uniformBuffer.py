from ...constants import _NP_FLOAT
from ..gl import GLObject, GLHelper

from OpenGL import GL
import numpy as np

class UniformBuffer(GLObject):
	def __init__(self, size: int, usage = GL.GL_STREAM_DRAW):
		super().__init__()
		self._id = GLHelper.CreateBuffer()
		
		GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self._id)
		GL.glBufferData(GL.GL_UNIFORM_BUFFER, size, None, usage)
		GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, 0)

		self.__size = size

	def Delete(self, removeRef: bool):
		super().Delete(removeRef)
		GL.glDeleteBuffers(1, [self._id])

	def Bind(self):
		GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self._id)

	def BindToUniform(self, index: int):
		GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, index, self._id)

	def AddData(self, data: list, size: int) -> None:
		GL.glNamedBufferSubData(self._id, 0, size, np.asarray(data, dtype=_NP_FLOAT))

	@property
	def Size(self):
		return self.__size