from .textureData import TextureData
from .textureSpec import TextureSpec
from ...debugging import Debug, LogLevel
from ...memory import GLMarshal

from OpenGL import GL
import numpy as np
import time
import ctypes

class Texture(object):
	def __init__(self, tData: TextureData, tSpec: TextureSpec):
		start = time.perf_counter()

		self.width = tData.width
		self.height = tData.height

		self.__id = np.empty(1, dtype=np.uint32)
		GL.glCreateTextures(GL.GL_TEXTURE_2D, 1, self.__id)
		GL.glTextureStorage2D(self.__id, tSpec.mipmaps, GL.GL_RGBA8, tData.width, tData.height)
		
		GL.glTextureParameteri(self.__id, GL.GL_TEXTURE_WRAP_S, tSpec.wrapMode)
		GL.glTextureParameteri(self.__id, GL.GL_TEXTURE_WRAP_T, tSpec.wrapMode)
		GL.glTextureParameteri(self.__id, GL.GL_TEXTURE_MIN_FILTER, tSpec.minFilter)
		GL.glTextureParameteri(self.__id, GL.GL_TEXTURE_MAG_FILTER, tSpec.magFilter)

		GL.glTextureSubImage2D(self.__id, 0, 0, 0, tData.width, tData.height, tData.format, GL.GL_UNSIGNED_BYTE, np.asarray(tData.data, dtype = np.uint8))
		GL.glGenerateTextureMipmap(self.__id)

		Debug.GetGLError()
		GLMarshal.AddObjectRef(self)
		Debug.Log(f"Texture (id: {self.__id}) initialized in {time.perf_counter() - start} seconds.", LogLevel.Info)

	def BindToUnit(self, slot):
		GL.glBindTextureUnit(slot, self.__id)

	def Delete(self, removeRef: bool):
		GL.glDeleteTextures(1, [self.__id])

		if removeRef:
			GLMarshal.RemoveObjectRef(self)
	
	@property
	def ID(self):
		return self.__id
	
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