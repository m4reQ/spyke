from spyke.enums import GLType
from spyke import debug
from .glBuffer import DynamicBuffer

from OpenGL import GL

class UniformBuffer(DynamicBuffer):
	def __init__(self, size: int, data_type: GLType):
		super().__init__(size, data_type)

	def bind(self) -> None:
		GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self.id)

	def bind_to_uniform(self, index: int) -> None:
		GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, index, self.id)