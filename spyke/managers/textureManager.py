#region Import
from ..utils import Static, Timer, ObjectManager
from ..debug import Log, LogLevel
from ..textureLoader import TextureLoader
from ..graphics.texturing.textureUtils import GetWhiteTexture, IMAGE_FORMAT_MAP
from ..graphics.texturing.texture import Texture, TextureData
from ..enums import TextureMagFilter

import os
from functools import lru_cache
from PIL import Image
from OpenGL import GL
#endregion

IMAGE_FORMAT_MAP = {
	"JPEG": GL.GL_RGB,
	"RGB": GL.GL_RGB,
	"PNG": GL.GL_RGBA,
	"RGBA": GL.GL_RGBA}

def LoadTexture(filepath: str):
	try:
		img = Image.open(filepath)
	except FileNotFoundError:
		raise RuntimeError(f"Cannot find image file: {filepath}.")

	texData = TextureData(img.size[0], img.size[1])

	texData.data = list(img.getdata())
	texData.format = IMAGE_FORMAT_MAP[img.mode]

	img.close()

	return texData

class TextureManager(Static):
	Textures = {}

	def LoadTexture(filepath: str, alias: str = None):
		name = alias if alias else filepath

		if name in TextureManager.Textures.keys():
			Log("Texture with given name already exists. Texture will be overwritten.", LogLevel.Warning)

			tex = TextureManager.Textures[name]
			ObjectManager.DeleteObject(tex)

			del TextureManager.Textures[name]

		textureData = LoadTexture(filepath)

		TextureManager.Textures[name] = Texture(textureData)