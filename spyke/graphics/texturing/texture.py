from .textureData import TextureData
from ...debugging import Log, LogLevel
from ...managers.objectManager import ObjectManager
from ...utils import Timer

from OpenGL import GL
import numpy

class Texture(object):
	def __init__(self, textureData: TextureData):
		Timer.Start()

		self.width = textureData.width
		self.height = textureData.height

		self.__id = GL.glGenTextures(1)
		
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.__id)

		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, textureData.minFilter)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, textureData.magFilter)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAX_LEVEL, textureData.mipLevels)
		
		GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.width, self.height, 0, textureData.format, GL.GL_UNSIGNED_BYTE, numpy.asarray(textureData.data, dtype = numpy.uint8))
		GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

		GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, 0)

		ObjectManager.AddObject(self)
		
		Log(f"Texture (id: {self.__id}) initialized in {Timer.Stop()} seconds.", LogLevel.Info)

	def BindToUnit(self, slot):
		GL.glBindTextureUnit(slot, self.__id)

	def Delete(self):
		GL.glDeleteTextures(1, [self.__id])
	
	@property
	def ID(self):
		return self.__id