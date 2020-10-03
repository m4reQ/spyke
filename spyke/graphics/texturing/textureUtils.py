from .textureHandle import TextureHandle

from OpenGL.GL import GL_RGB, GL_RGBA
import numpy

class TextureType:
	Rgb = GL_RGB
	Rgba = GL_RGBA

class TextureData(object):
	def __init__(self):
		self.Width = 0
		self.Height = 0
		self.Data = []
		self.TextureType = None
		self.ImageName = ""

def GenRawTextureData(width: int, height: int, textureType: TextureType):
	if textureType == TextureType.Rgb:
		extData = [255, 255, 255]
	elif textureType == TextureType.Rgba:
		extData = [255, 255, 255, 255]
	else:
		raise RuntimeError(f"Invalid texture type: {textureType}.")
	
	return numpy.asarray(extData * width * height, dtype = "uint8")

IMAGE_FORMAT_MAP = {
	"JPEG": TextureType.Rgb,
	"RGB": TextureType.Rgb,
	"PNG": TextureType.Rgba,
	"RGBA": TextureType.Rgba}

WhiteTexture = TextureHandle(0.001, 0.001, 0.0)