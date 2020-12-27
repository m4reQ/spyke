from ..utils import GetGLTypeSize, GetPointer, ObjectManager

from OpenGL import GL

class VertexArrayLayout:
	def __init__(self, index, count, type, normalized):
		self.Index = index
		self.Count = count
		self.Type = type
		self.IsNormalized = normalized

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
	
	def AddMat4Layout(self, index: int, _type: int, isNormalized: int):
		for i in range(4):
			GL.glVertexAttribPointer(index + i, 4, type, isNormalized, self.__vertexSize, GetPointer(self.__offset))
			GL.glEnableVertexAttribArray(index + i)

			self.__offset += GetGLTypeSize(_type) * 4

	def AddLayout(self, layout: VertexArrayLayout):
		GL.glVertexAttribPointer(layout.Index, layout.Count, layout.Type, layout.IsNormalized, self.__vertexSize, GetPointer(self.__offset))
		GL.glEnableVertexAttribArray(layout.Index)

		self.__offset += GetGLTypeSize(layout.Type) * layout.Count
	
	def AddLayouts(self, layouts: list):
		for layout in layouts:
			self.AddLayout(layout)

	def Bind(self):
		GL.glBindVertexArray(self.__id)
	
	def Delete(self):
		GL.glDeleteVertexArrays(1, [self.__id])
	
	@property
	def ID(self):
		return self.__id