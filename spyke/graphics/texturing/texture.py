from ...debugging import Debug, LogLevel
from ...constants import _NP_BYTE
from ..gl import GLObject, GLHelper

from OpenGL import GL
import numpy as np
import time

class TextureData(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.data = []
		self.format = GL.GL_RGB

class TextureSpec(object):
    def __init__(self):
        self.mipmaps = 2
        self.minFilter = GL.GL_LINEAR_MIPMAP_LINEAR
        self.magFilter = GL.GL_LINEAR
        self.wrapMode = GL.GL_REPEAT
		
class Texture(GLObject):
	def __init__(self, tData: TextureData, tSpec: TextureSpec):
		start = time.perf_counter()

		super().__init__()

		self.width = tData.width
		self.height = tData.height

		self._id = GLHelper.CreateTexture(GL.GL_TEXTURE_2D)
		GL.glTextureStorage2D(self._id, tSpec.mipmaps, GL.GL_RGBA8, tData.width, tData.height)
		
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_WRAP_S, tSpec.wrapMode)
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_WRAP_T, tSpec.wrapMode)
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_MIN_FILTER, tSpec.minFilter)
		GL.glTextureParameteri(self._id, GL.GL_TEXTURE_MAG_FILTER, tSpec.magFilter)

		GL.glTextureSubImage2D(self._id, 0, 0, 0, tData.width, tData.height, tData.format, GL.GL_UNSIGNED_BYTE, np.asarray(tData.data, dtype = _NP_BYTE))
		GL.glGenerateTextureMipmap(self._id)

		Debug.GetGLError()
		Debug.Log(f"Texture (id: {self._id}) initialized in {time.perf_counter() - start} seconds.", LogLevel.Info)

	def BindToUnit(self, slot) -> None:
		GL.glBindTextureUnit(slot, self._id)

	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteTextures(1, [self._id])
	
	@classmethod
	def CreateWhiteTexture(cls):
		data = TextureData(1, 1)
		
		data.data = [255, 255, 255, 255]
		data.format = GL.GL_RGBA

		spec = TextureSpec()
		spec.minFilter = GL.GL_NEAREST
		spec.magFilter = GL.GL_NEAREST
		spec.mipmaps = 1

		return cls(data, spec)