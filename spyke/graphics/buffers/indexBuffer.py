from ...utils import ObjectManager, INT_SIZE

from OpenGL import GL
import numpy

class IndexBuffer(object):
	def __init__(self, data: list):
		self.__size = len(data) * INT_SIZE
		self.__id = GL.glGenBuffers(1)
		
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.__id)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.__size, numpy.asarray(data, dtype=numpy.int32), GL.GL_STATIC_DRAW)
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

		ObjectManager.AddObject(self)
	
	def Bind(self) -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.__id)
	
	def Unbind(self) -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
	
	def Delete(self) -> None:
		GL.glDeleteBuffers(1, [self.__id])
	
	@property
	def Size(self):
		return self.__size
	
	@property
	def ID(self):
		return self.__id
	
	@staticmethod
	def UnbindAll() -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)