from ...utils import INT_SIZE, GetPointer, ObjectManager
from ...enums import BufferUsageFlag

from OpenGL import GL
import numpy

class DynamicVertexBuffer(object):
	def __init__(self, size, usage = BufferUsageFlag.StreamDraw):
		self.__size = size
		self.__id = GL.glGenBuffers(1)

		self.__usageFlag = usage
		
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.__id)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.__size, None, self.__usageFlag)
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

		ObjectManager.AddObject(self)

	def AddData(self, data, size):
		GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, size, numpy.asarray(data, dtype=numpy.float32))
	
	def Bind(self):
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.__id)
	
	def Delete(self):
		GL.glDeleteBuffers(1, [self.__id])
	
	def Clear(self):
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.__size, None, self.__usageFlag)
	
	@property
	def Size(self):
		return self.__size
	
	@property
	def ID(self):
		return self.__id

class StaticIndexBuffer(object):
	def __init__(self, data: list):
		self.__size = len(data) * INT_SIZE
		self.__id = GL.glGenBuffers(1)
		
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.__id)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.__size, numpy.asarray(data, dtype=numpy.int32), GL.GL_STATIC_DRAW)
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

		ObjectManager.AddObject(self)
	
	def Bind(self):
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.__id)
	
	def Delete(self):
		GL.glDeleteBuffers(1, [self.__id])
	
	@property
	def Size(self):
		return self.__size
	
	@property
	def ID(self):
		return self.__id