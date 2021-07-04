from .aBuffer import ABuffer
from ..gl import GLHelper
from ...constants import _NP_FLOAT

from OpenGL import GL
import numpy as np

class TextureBuffer(ABuffer):
	_BufferUsageFlags = GL.GL_DYNAMIC_STORAGE_BIT
	
	def __init__(self, size: int, format: GL.GLenum, dataStorageView: memoryview):
		super().__init__(size)
	
		self._texId = GLHelper.CreateTexture(GL.GL_TEXTURE_BUFFER)
		self._dataView = dataStorageView

		GL.glNamedBufferStorage(self._id, self._size, None, TextureBuffer._BufferUsageFlags)
		GL.glTextureBuffer(self._texId, format, self._id)
	
	def TransferData(self, size: int) -> None:
		"""
		Transfer given amount of data from bound data storage
		to buffer's memory.
		"""

		GL.glNamedBufferSubData(self._id, 0, size, self._dataView.obj)

	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteTextures(1, [self._texId])
	
	@property
	def TextureID(self):
		return self._texId