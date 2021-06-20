from ..gl import GLObject, GLHelper
from ...constants import _NP_FLOAT

from OpenGL import GL
import numpy as np

class TextureBuffer(GLObject):
	def __init__(self, size: int, format: GL.GLenum, usage = GL.GL_STREAM_DRAW):
		super().__init__()
		
		self.__size = size

		self._id = GLHelper.CreateBuffer()
		self._texId = GLHelper.CreateTexture(GL.GL_TEXTURE_BUFFER)

		GL.glNamedBufferData(self._id, size, None, usage)
		GL.glTextureBuffer(self._texId, format, self._id)
	
	def AddData(self, data: list, size: int) -> None:
		GL.glNamedBufferSubData(self._id, 0, size, np.asarray(data, dtype=_NP_FLOAT))

	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteBuffers(1, [self._id])
		GL.glDeleteTextures(1, [self._texId])
	
	@property
	def Size(self):
		return self.__size
	
	@property
	def TextureID(self):
		return self._texId