from ..debugging import Debug, LogLevel
from spyke.graphics import gl
from ..constants import _GL_TYPE_SIZE_MAP

from OpenGL import GL

class VertexArray(gl.GLObject):
	def __init__(self):
		super().__init__()

		self._id = gl.create_vertex_array()

		self._offsets = {}
	
	def BindVertexBuffer(self, bindingIndex: int, bufferId: int, offset: int, stride: int) -> None:
		GL.glVertexArrayVertexBuffer(self.id, bindingIndex, bufferId, offset, stride)
	
	def BindElementBuffer(self, bufferId: int) -> None:
		GL.glVertexArrayElementBuffer(self.id, bufferId)
	
	def AddLayout(self, attribIndex: int, bindingIndex: int, count: int, _type: GL.GLenum, isNormalized: bool, divisor: int = 0) -> None:
		if bindingIndex in self._offsets:
			offset = self._offsets[bindingIndex]
		else:
			offset = 0
			self._offsets[bindingIndex] = 0

		GL.glEnableVertexArrayAttrib(self.id, attribIndex)
		GL.glVertexArrayAttribFormat(self.id, attribIndex, count, _type, isNormalized, offset)
		GL.glVertexArrayBindingDivisor(self.id, bindingIndex, divisor)
		GL.glVertexArrayAttribBinding(self.id, attribIndex, bindingIndex)

		self._offsets[bindingIndex] += _GL_TYPE_SIZE_MAP[_type] * count
	
	def AddMatrixLayout(self, attribIndex: int, bindingIndex: int, cols: int, rows: int, _type: GL.GLenum, isNormalized: bool, divisor: int = 0) -> None:
		for i in range(rows):
			self.AddLayout(attribIndex + i, bindingIndex, cols, _type, isNormalized, divisor)
	
	def Bind(self) -> None:
		GL.glBindVertexArray(self.id)
	
	def delete(self) -> None:
		GL.glDeleteVertexArrays(1, [self.id])