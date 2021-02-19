#region Import
from ...managers.objectManager import ObjectManager
from ...constants import _INT_SIZE

from OpenGL import GL
import numpy
#endregion

class IndexBuffer(object):
	@staticmethod
	def CreateQuadIndices(count: int) -> list:
		data = []

		offset = 0
		i = 0
		while i < count:
			data.extend([
				0 + offset,
				1 + offset,
				2 + offset,
				2 + offset,
				3 + offset,
				0 + offset])
			
			offset += 4
			i += 6
		
		return data
		
	def __init__(self, data: list):
		self.__size = len(data) * _INT_SIZE
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