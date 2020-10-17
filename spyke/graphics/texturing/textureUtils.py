from ...enums import TextureType

import numpy

class TextureData(object):
	def __init__(self):
		self.Width = 0
		self.Height = 0
		self.Data = []
		self.TextureType = None
		self.ImageName = ""

class TextureHandle(object):
	def __init__(self, u: float, v: float, index: float, arrayId: int):
		self.U = u
		self.V = v
		self.Index = index
		self.TexarrayID = arrayId
		self.Width = 0
		self.Height = 0

def GetWhiteTexture():
	data = TextureData()
	data.Width = 1
	data.Height = 1
	data.Data = [255, 255, 255]
	data.TextureType = TextureType.Rgb

	return data

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