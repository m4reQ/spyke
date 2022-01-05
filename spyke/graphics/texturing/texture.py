from spyke.enums import InternalFormat
from spyke.graphics import gl
from spyke import debug

from OpenGL import GL
import numpy as np
import time

class TextureData:
	__slots__ = (
		'__weakref__',
		'width',
		'height',
		'data',
		'format',
		'filepath'
	)
	
	# TODO: Use specific enums for type hints
	def __init__(self, width: int, height: int):
		self.width: int = width
		self.height: int = height
		self.data: np.ndarray = None
		self.format: GL.GLenum = GL.GL_RGBA
		self.filepath: str = ""

class TextureSpec:
	__slots__ = (
		'__weakref__',
		'mipmaps',
		'min_filter',
		'mag_filter',
		'wrap_mode',
		'compress'
	)
	
	# TODO: Use specific enums for type hints
	def __init__(self):
		self.mipmaps: int = 3
		self.min_filter: GL.GLenum = GL.GL_LINEAR_MIPMAP_LINEAR
		self.mag_filter: GL.GLenum = GL.GL_LINEAR
		self.wrap_mode: GL.GLenum = GL.GL_REPEAT
		self.compress: bool = True
		
class Texture(gl.GLObject):
	_InternalFormat = GL.GL_RGBA8
	_CompressedInternalFormat = GL.GL_COMPRESSED_RGBA
	_CompressionEnabled = False

	def __init__(self, tData: TextureData, tSpec: TextureSpec):
		start = time.perf_counter()

		super().__init__()

		self.width = tData.width
		self.height = tData.height

		self.filepath = tData.filepath
		self.specification = tSpec

		self._id = gl.create_texture(GL.GL_TEXTURE_2D)

		_format = Texture._CompressedInternalFormat if tSpec.compress and Texture._CompressionEnabled else Texture._InternalFormat

		GL.glTextureStorage2D(self.id, tSpec.mipmaps, _format, tData.width, tData.height)
		
		GL.glTextureParameteri(self.id, GL.GL_TEXTURE_WRAP_S, tSpec.wrap_mode)
		GL.glTextureParameteri(self.id, GL.GL_TEXTURE_WRAP_T, tSpec.wrap_mode)
		GL.glTextureParameteri(self.id, GL.GL_TEXTURE_MIN_FILTER, tSpec.min_filter)
		GL.glTextureParameteri(self.id, GL.GL_TEXTURE_MAG_FILTER, tSpec.mag_filter)

		GL.glTextureSubImage2D(self.id, 0, 0, 0, tData.width, tData.height, tData.format, GL.GL_UNSIGNED_BYTE, tData.data)
		GL.glGenerateTextureMipmap(self.id)

		is_compressed = GL.GLint()
		GL.glGetTextureLevelParameteriv(self.id, 0, GL.GL_TEXTURE_COMPRESSED, is_compressed)
		self._is_compressed = True if is_compressed.value else False

		debug.get_gl_error()
		debug.log_info(f'{self} initialized in {time.perf_counter() - start} seconds.')

	def bind_to_unit(self, slot) -> None:
		GL.glBindTextureUnit(slot, self.id)

	def delete(self) -> None:
		GL.glDeleteTextures(1, [self.id])
	
	@classmethod
	def CreateWhiteTexture(cls):
		tData = TextureData(1, 1)

		tData.data = np.array([255, 255, 255, 255], dtype=np.ubyte)
		tData.format = GL.GL_RGBA

		spec = TextureSpec()
		spec.min_filter = GL.GL_NEAREST
		spec.mag_filter = GL.GL_NEAREST
		spec.mipmaps = 1
		spec.compress = False

		return cls(tData, spec)
	
	@property
	def is_compressed(self) -> bool:
		return self._is_compressed