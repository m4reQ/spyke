from .aBuffer import ABuffer

from OpenGL import GL

class UniformBuffer(ABuffer):
	_BufferStorageFlags = GL.GL_DYNAMIC_STORAGE_BIT

	def __init__(self, size: int):
		super().__init__(size, None)

		GL.glNamedBufferStorage(self.id, self._size, None, self._BufferStorageFlags)

	def Bind(self):
		GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self.id)

	def BindToUniform(self, index: int):
		GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, index, self.id)

	def AddData(self, data: memoryview, size: int) -> None:
		GL.glNamedBufferSubData(self.id, 0, size, data.obj)
		data.release()