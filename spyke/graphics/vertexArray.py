from spyke import debug
from spyke.graphics import gl
from spyke.graphics.buffers import ABuffer
from spyke.utils import convert
from spyke.enums import GLType
from ..constants import _GL_TYPE_SIZE_MAP

from OpenGL import GL

class VertexArray(gl.GLObject):
	def __init__(self):
		super().__init__()

		self._id = gl.create_vertex_array()

		self._offsets = {}

		debug.log_info(f'{self} created succesfully.')
	
	def BindVertexBuffer(self, binding_index: int, buffer: ABuffer, offset: int, stride: int) -> None:
		GL.glVertexArrayVertexBuffer(self.id, binding_index, buffer.id, offset, stride)
	
	def BindElementBuffer(self, buffer: ABuffer) -> None:
		GL.glVertexArrayElementBuffer(self.id, buffer.id)
	
	def AddLayout(self, attrib_index: int, binding_index: int, count: int, _type: GLType, is_normalized: bool, divisor: int = 0) -> None:
		if binding_index in self._offsets:
			offset = self._offsets[binding_index]
		else:
			offset = 0
			self._offsets[binding_index] = 0

		GL.glEnableVertexArrayAttrib(self.id, attrib_index)
		GL.glVertexArrayAttribFormat(self.id, attrib_index, count, _type, is_normalized, offset)
		GL.glVertexArrayBindingDivisor(self.id, binding_index, divisor)
		GL.glVertexArrayAttribBinding(self.id, attrib_index, binding_index)

		self._offsets[binding_index] += convert.gl_type_to_size(_type) * count
	
	def AddMatrixLayout(self, attrib_index: int, binding_index: int, cols: int, rows: int, _type: GLType, is_normalized: bool, divisor: int = 0) -> None:
		for i in range(rows):
			self.AddLayout(attrib_index + i, binding_index, cols, _type, is_normalized, divisor)
	
	def Bind(self) -> None:
		GL.glBindVertexArray(self.id)
	
	def delete(self) -> None:
		GL.glDeleteVertexArrays(1, [self.id])