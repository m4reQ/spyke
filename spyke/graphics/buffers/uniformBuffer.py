from ...constants import _NP_FLOAT
from .aBuffer import ABuffer

from OpenGL import GL
import numpy as np

class UniformBuffer(ABuffer):
	_BufferStorageFlags = GL.GL_DYNAMIC_STORAGE_BIT

	def __init__(self, size: int, usage = GL.GL_STREAM_DRAW):
		super().__init__(size)

		GL.glNamedBufferStorage(self._id, self._size, None, UniformBuffer._BufferStorageFlags)

	def Bind(self):
		GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self._id)

	def BindToUniform(self, index: int):
		GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, index, self._id)

	def AddData(self, data: memoryview, size: int) -> None:
		GL.glNamedBufferSubData(self._id, 0, size, data.obj)
		data.release()