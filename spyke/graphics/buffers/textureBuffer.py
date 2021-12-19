from .aBuffer import ABuffer, AMappable
from spyke.graphics import gl

from OpenGL import GL

class TextureBuffer(ABuffer):
	_BufferUsageFlags = GL.GL_DYNAMIC_STORAGE_BIT
	
	def __init__(self, size: int, format: GL.GLenum, dataStorageView: memoryview):
		super().__init__(size, None)
	
		self._texId = gl.create_texture(GL.GL_TEXTURE_BUFFER)
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
	
	def __del__(self):
		self._dataView.release()
	
	@property
	def TextureID(self):
		return self._texId

class MappedTextureBuffer(AMappable):
	def __init__(self, size: int, format: GL.GLenum):
		super().__init__(size, None)
	
		self._tex_id = gl.create_texture(GL.GL_TEXTURE_BUFFER)

		GL.glNamedBufferStorage(self.id, self._size, None, self._BufferUsageFlags)
		GL.glTextureBuffer(self.texture_id, format, self.id)

		self._MapPersistent()
	
	def TransferData(self, size: int) -> None:
		"""
		Transfer given amount of data from bound data storage
		to buffer's memory.
		"""

		GL.glNamedBufferSubData(self.id, 0, size, self._dataView.obj)

	def delete(self) -> None:
		super().delete()
		GL.glDeleteTextures(1, [self.texture_id])
	
	@property
	def texture_id(self) -> int:
		return self._tex_id.value