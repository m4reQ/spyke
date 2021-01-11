from ...utils import ObjectManager

from OpenGL import GL
import numpy

class VertexBuffer(object):
	def __init__(self, size: int, usage = GL.GL_STREAM_DRAW):
		self.__size = size
		self.__id = GL.glGenBuffers(1)

		self.__usageFlag = usage
		
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.__id)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.__size, None, self.__usageFlag)
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

		ObjectManager.AddObject(self)

	def AddData(self, data: list, size: int) -> None:
		GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, size, numpy.asarray(data, dtype=numpy.float32))
	
	def Bind(self) -> None:
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.__id)
	
	def Unbind(self) -> None:
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
	
	def Delete(self) -> None:
		GL.glDeleteBuffers(1, [self.__id])
	
	def Clear(self) -> None:
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.__size, None, self.__usageFlag)

	#region Direct State Access
	def AddDataDirect(self, data: list, size: int) -> None:
		GL.glNamedBufferSubData(self.__id, 0, size, numpy.asarray(data, dtype=numpy.float32))
	
	def ClearDirect(self) -> None:
		GL.glNamedBufferData(self.__id, self.__size, None, self.__usageFlag)
	#endregion
	
	@property
	def Size(self):
		return self.__size
	
	@property
	def ID(self):
		return self.__id
	
	@staticmethod
	def UnbindAll() -> None:
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)