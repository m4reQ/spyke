from ..utils import GetGLTypeSize, GetPointer
from ..managers.objectManager import ObjectManager

from OpenGL import GL

class VertexArray(object):
	def __init__(self):
		self.__vertexSize = 0

		self.__id = GL.glGenVertexArrays(1)
		self.__offset = 0

		ObjectManager.AddObject(self)
	
	def SetVertexSize(self, size: int):
		self.__vertexSize = size

	def ClearVertexOffset(self):
		self.__offset = 0
	
	def AddDivisor(self, index: int, instances: int):
		GL.glVertexAttribDivisor(index, instances)
	
	def AddLayout(self, index: int, count: int, _type: int, isNormalized: bool, divisor = 0):
		GL.glVertexAttribPointer(index, count, _type, isNormalized, self.__vertexSize, GetPointer(self.__offset))
		GL.glEnableVertexAttribArray(index)

		if divisor:
			GL.glVertexAttribDivisor(index, divisor)

		self.__offset += GetGLTypeSize(_type) * count

	def Bind(self):
		GL.glBindVertexArray(self.__id)
	
	def Delete(self):
		GL.glDeleteVertexArrays(1, [self.__id])
	
	@property
	def ID(self):
		return self.__id