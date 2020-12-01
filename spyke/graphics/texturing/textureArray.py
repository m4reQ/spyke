#region Import
from .textureUtils import TextureData, TextureHandle
from ... import USE_FAST_MIN_FILTER
from ...utils import ObjectManager, Timer
from ...enums import TextureType, TextureMagFilter
from ...debug import Log, LogLevel

import numpy
from OpenGL import GL
#endregion

class TextureArray(object):
	__MaxLayersCount = 0

	__TextureType = TextureType.Rgba
	__InternalFormat = GL.GL_RGBA8
	__Pixeltype = GL.GL_UNSIGNED_BYTE

	if USE_FAST_MIN_FILTER:
		__MinFilter = GL.GL_NEAREST_MIPMAP_LINEAR
	else:
		__MinFilter = GL.GL_LINEAR_MIPMAP_LINEAR

	def __init__(self, maxWidth: int, maxHeight: int, layersCount: int, mipmapLevels: int = 2, magFilter: TextureMagFilter = TextureMagFilter.Linear, isBlank = False):
		Timer.Start()

		if not TextureArray.__MaxLayersCount:
			TextureArray.__MaxLayersCount = int(GL.glGetInteger(GL.GL_MAX_ARRAY_TEXTURE_LAYERS))
		
		if layersCount > TextureArray.__MaxLayersCount:
			raise RuntimeError(f"Cannot create texture array with {layersCount} layers (max. layers count: {TextureArray.__MaxLayersCount}).")

		self.__maxWidth = maxWidth
		self.__maxHeight = maxHeight
		self.__layers = layersCount
		self.__mipmapLevels = mipmapLevels
		self.__isBlank = isBlank

		self.__currentLayer = 0
		
		self.MagFilter = magFilter

		self.canWrite = True

		self.__id = GL.glGenTextures(1)
		GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, self.__id)
		GL.glTexStorage3D(GL.GL_TEXTURE_2D_ARRAY, self.__mipmapLevels, TextureArray.__InternalFormat, self.__maxWidth, self.__maxHeight, self.__layers)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MIN_FILTER, TextureArray.__MinFilter)
		GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MAG_FILTER, magFilter)

		GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, 0)

		ObjectManager.AddObject(self)

		Log(f"Texture array of size ({self.__maxWidth}x{self.__maxHeight}x{self.__layers}) initialized in {Timer.Stop()} seconds.", LogLevel.Info)
	
	def UploadTexture(self, texData: TextureData) -> TextureHandle:
		self.canWrite = False

		self.Bind()

		if self.__currentLayer + 1 > TextureArray.__MaxLayersCount:
			raise RuntimeError("Max texture array layers count exceeded.")
		if texData.Width > self.__maxWidth or texData.Height > self.__maxHeight:
			raise RuntimeError("Texture size is higher than maximum.")
		
		if texData.Width != self.__maxWidth or texData.Height != self.__maxHeight:
			GL.glTexSubImage3D(GL.GL_TEXTURE_2D_ARRAY, 0, 0, 0, self.__currentLayer, self.__maxWidth, self.__maxHeight, 1, TextureArray.__TextureType, TextureArray.__Pixeltype, numpy.empty(self.__maxWidth * self.__maxHeight * (3 if TextureArray.__TextureType == TextureType.Rgb else 4), dtype = numpy.uint8))
		GL.glTexSubImage3D(GL.GL_TEXTURE_2D_ARRAY, 0, 0, 0, self.__currentLayer, texData.Width, texData.Height, 1, texData.TextureType, TextureArray.__Pixeltype, numpy.asarray(texData.Data, dtype = numpy.uint8))
		GL.glGenerateMipmap(GL.GL_TEXTURE_2D_ARRAY)

		handle = TextureHandle((texData.Width - 0.5) / self.__maxWidth, (texData.Height - 0.5) / self.__maxHeight, self.__currentLayer)
		handle.Width = texData.Width
		handle.Height = texData.Height

		self.__currentLayer += 1

		self.canWrite = True

		return handle
	
	@staticmethod
	def UnbindAll():
		GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, 0)
	
	def Bind(self):
		GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, self.__id)
	
	def Delete(self):
		GL.glDeleteTextures(1, [self.__id])
	
	#region Getters
	@property
	def CurrentLayer(self):
		return self.__currentLayer
	
	@property
	def IsAccepting(self):
		return self.__currentLayer < self.__layers
	
	@property
	def Width(self):
		return self.__maxWidth
	
	@property
	def Height(self):
		return self.__maxHeight
	
	@property
	def Layers(self):
		return self.__layers
	
	@property
	def Levels(self):
		return self.__mipmapLevels
	
	@property
	def IsBlank(self):
		return self.__isBlank
	#endregion