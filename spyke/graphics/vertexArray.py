from .gl import GLObject, GLHelper
from ..constants import _GL_TYPE_SIZE_MAP

from OpenGL import GL
import ctypes

class VertexArray(GLObject):
	def __init__(self):
		super().__init__()
		self._id = GL.glGenVertexArrays(1)#GLHelper.CreateVertexArray()
		
		self.__vertexSize = 0
		self.__offset = 0
	
	def SetVertexSize(self, size: int):
		self.__vertexSize = size

	def ClearVertexOffset(self):
		self.__offset = 0
	
	def AddDivisor(self, index: int, instances: int):
		GL.glVertexAttribDivisor(index, instances)
	
	def AddLayout(self, index: int, count: int, _type: int, isNormalized: bool, divisor: int = 0):
		GL.glVertexAttribPointer(index, count, _type, isNormalized, self.__vertexSize, ctypes.c_void_p(self.__offset))
		GL.glEnableVertexAttribArray(index)

		GL.glVertexAttribDivisor(index, divisor)

		self.__offset += _GL_TYPE_SIZE_MAP[_type] * count

	def Bind(self) -> None:
		GL.glBindVertexArray(self._id)
	
	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteVertexArrays(1, [self._id])