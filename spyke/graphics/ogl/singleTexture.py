from ..textureLoader import TextureLoader
from .objectManager import ObjectManager
from ..debug import Log, LogLevel

from OpenGL import GL
from time import perf_counter
import numpy

class SingleTexture(object):
	__InternalFormat = GL.GL_RGBA8
	__MinFilter = GL.GL_LINEAR_MIPMAP_NEAREST
	__MinFastFilter = GL.GL_NEAREST_MIPMAP_LINEAR
	__MipmapLevels = 4

	def __init__(self, filepath: str):
		start = perf_counter()
		self.__id = GL.glGenTextures(1)

		data = TextureLoader.LoadTexture(filepath)

		self.width = data.Width
		self.height = data.Height

		GL.glBindTexture(GL.GL_TEXTURE_2D, self.__id)
		GL.glTexStorage2D(GL.GL_TEXTURE_2D, SingleTexture.__MipmapLevels, SingleTexture.__InternalFormat, data.Width, data.Height)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MIN_FILTER, SingleTexture.__MinFilter)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
		GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, 0, 0, data.Width, data.Height, data.TextureType, GL.GL_UNSIGNED_BYTE, numpy.asarray(data.Data, dtype = "uint8"))
		GL.glGenerateMipmap(GL.GL_TEXTURE_2D)
		GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

		ObjectManager.AddObject(self)

		Log(f"Texture '{filepath}' uploaded in {perf_counter() - start} seconds.", LogLevel.Info)
	
	def Bind(self):
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.__id)
	
	def Delete(self):
		GL.glDeleteTextures(1, [self.__id])
	
	@property
	def ID(self):
		return self.__id