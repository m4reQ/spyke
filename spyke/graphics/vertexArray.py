from ..debugging import Debug, LogLevel
from .gl import GLObject, GLHelper
from ..constants import _GL_TYPE_SIZE_MAP

from OpenGL import GL
import ctypes

class VertexArray(GLObject):
	def __init__(self):
		super().__init__()

		self._id = GLHelper.CreateVertexArray()
		self._offsets = {}
		self._bindings = {}
	
	def BindVertexBuffer(self, bindingIndex: int, bufferId: int, offset: int, stride: int) -> None:
		if bindingIndex in self._bindings:
			Debug.Log(f"Vertex buffer binding already exists at binding point {bindingIndex}. This binding will be overwritten by buffer with id {bufferId}.", LogLevel.Info)
		self._bindings[bindingIndex] = bufferId

		GL.glVertexArrayVertexBuffer(self._id, bindingIndex, bufferId, offset, stride)
	
	def BindElementBuffer(self, bufferId: int) -> None:
		GL.glVertexArrayElementBuffer(self._id, bufferId)
	
	def AddLayout(self, attribIndex: int, bindingIndex: int, count: int, _type: GL.GLenum, isNormalized: bool, divisor: int = 0) -> None:
		if bindingIndex in self._offsets:
			offset = self._offsets[bindingIndex]
		else:
			offset = 0
			self._offsets[bindingIndex] = 0

		GL.glEnableVertexArrayAttrib(self._id, attribIndex)
		GL.glVertexArrayAttribFormat(self._id, attribIndex, count, _type, isNormalized, offset)
		GL.glVertexArrayBindingDivisor(self._id, bindingIndex, divisor)
		GL.glVertexArrayAttribBinding(self._id, attribIndex, bindingIndex)

		self._offsets[bindingIndex] += _GL_TYPE_SIZE_MAP[_type] * count
	
	def AddMatrixLayout(self, attribIndex: int, bindingIndex: int, cols: int, rows: int, _type: GL.GLenum, isNormalized: bool, divisor: int = 0) -> None:
		for i in range(rows):
			self.AddLayout(attribIndex + i, bindingIndex, cols, _type, isNormalized, divisor)
	
	def Bind(self) -> None:
		GL.glBindVertexArray(self._id)
	
	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)