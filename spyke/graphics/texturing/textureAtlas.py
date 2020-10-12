raise NotImplementedError("Module not implemented yet")

from .textureUtils import TextureData
from ...utils import ObjectManager
from ...debug import Log, LogLevel, Timer

from OpenGL import GL

class TextureAtlas(object):
	__InternalFormat = GL.GL_RGBA8
	__MinFilter = GL.GL_LINEAR_MIPMAP_NEAREST
	__MinFastFilter = GL.GL_NEAREST_MIPMAP_LINEAR
	__Pixeltype = GL.GL_UNSIGNED_BYTE

	def __init__(self, width, height):
		self.__width = width
		self.__height = height

		self.__id = GL.glGenTextures(1)

		GL.glBindTexture(GL.GL_TEXTURE_2D, self.__id)
		GL.glTexStorage2D(GL.GL_TEXTURE_2D, 0, TextureAtlas.__InternalFormat, self.__width, self.__height)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, TextureAtlas.__MinFilter)
		GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
		GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

		self.lastWidth = 0
		self.lastHeight = 0

		ObjectManager.AddObject(self)
	
	def UploadTexture(self, data: TextureData):
		Timer.Start()

		if self.lastWidth + data.Width > self.__width and self.lastHeight + data.Height > self.__height:
			raise RuntimeError("Cannot insert texture into atlass. Insufficient size.")
		
		posX = 0
		posY = 0

		if self.lastWidth + data.Width <= self.__width:
			posX = self.lastWidth
			self.lastWidth += data.Width
		else:
			posX = 0
			self.lastWidth = 0
			posY = self.lastHeight
		
		GL.glBindTexture(GL.GL_TEXTURE_2D, self.__id)
		GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, posX, posY, data.Width, data.Height, data.TextureType, TextureAtlas.__Pixeltype, data.Data)

		u = (posX - 0.5) / self.__width
		v = (posY - 0.5) / self.__height

		atlWidth = (data.Width - 0.5) / self.__width
		atlHeight = (data.Height - 0.5) / self.__height

		Log(f"Texture '{data.ImageName}' uploaded in {Timer.Stop()} seconds.", LogLevel.Info)

		return TextureHandle(u, v, atlWidth, atlHeight, self.__id)