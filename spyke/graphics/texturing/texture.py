from ...debugging import Debug, LogLevel
from ...constants import _NP_UBYTE
from ..gl import GLObject, GLHelper

from OpenGL import GL
import numpy as np
import time

class TextureData(object):
	__slots__ = ("width", "height", "data", "format", "filepath", "__weakref__")
	
	def __init__(self, width: int, height: int):
		self.width: int = width
		self.height: int = height
		self.data: memoryview = None
		self.format: GL.GLenum = GL.GL_RGB
		self.filepath: str = ""

class TextureSpec(object):
	__slots__ = ("mipmaps", "minFilter", "magFilter", "wrapMode", "compress", "__weakref__")

	def __init__(self):
		self.mipmaps: int = 3
		self.minFilter: GL.GLenum = GL.GL_LINEAR_MIPMAP_LINEAR
		self.magFilter: GL.GLenum = GL.GL_LINEAR
		self.wrapMode: GL.GLenum = GL.GL_REPEAT
		self.compress: bool = True
		
class Texture(GLObject):
	_InternalFormat = GL.GL_RGBA8
	_CompressedInternalFormat = GL.GL_COMPRESSED_RGBA

	def __init__(self, tData: TextureData, tSpec: TextureSpec):
		start = time.perf_counter()

		super().__init__()

		self.width = tData.width
		self.height = tData.height

		self.filepath = tData.filepath
		self.specification = tSpec

		self._id = GLHelper.CreateTexture(GL.GL_TEXTURE_2D)

		_format = Texture._CompressedInternalFormat if tSpec.compress else Texture._InternalFormat

		GL.glTextureStorage2D(self._id, tSpec.mipmaps, _format, tData.width, tData.height)
		
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_WRAP_S, tSpec.wrapMode)
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_WRAP_T, tSpec.wrapMode)
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_MIN_FILTER, tSpec.minFilter)
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_MAG_FILTER, tSpec.magFilter)

		GL.glTextureSubImage2D(self._id, 0, 0, 0, tData.width, tData.height, tData.format, GL.GL_UNSIGNED_BYTE, tData.data.obj)
		GL.glGenerateTextureMipmap(self._id)

		tData.data.release()

		Debug.GetGLError()
		Debug.Log(f"Texture (id: {self._id}) initialized in {time.perf_counter() - start} seconds.", LogLevel.Info)

	def BindToUnit(self, slot) -> None:
		GL.glBindTextureUnit(slot, self._id)

	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteTextures(1, [self._id])
	
	@classmethod
	def CreateWhiteTexture(cls):
		tData = TextureData(1, 1)

		tData.data = memoryview(np.array([255, 255, 255, 255], dtype=_NP_UBYTE))
		tData.format = GL.GL_RGBA

		spec = TextureSpec()
		spec.minFilter = GL.GL_NEAREST
		spec.magFilter = GL.GL_NEAREST
		spec.mipmaps = 1
		spec.compress = False

		return cls(tData, spec)