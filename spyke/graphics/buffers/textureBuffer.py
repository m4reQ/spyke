from spyke.graphics import gl
from spyke.enums import GLType, InternalFormat
from .glBuffer import DynamicBuffer

from OpenGL import GL

class TextureBuffer(DynamicBuffer):
	def __init__(self, size: int, data_type: GLType, format: InternalFormat):
		super().__init__(size, data_type)
	
		self._tex_id = gl.create_texture(GL.GL_TEXTURE_BUFFER)
		GL.glTextureBuffer(self.texture_id, format, self.id)

	def delete(self) -> None:
		super().delete()
		GL.glDeleteTextures(1, [self.texture_id])
	
	@property
	def texture_id(self) -> int:
		return self._tex_id.value