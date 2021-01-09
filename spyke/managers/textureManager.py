#region Import
from ..utils import Static, Timer, ObjectManager
from ..debug import Log, LogLevel
from ..textureLoader import TextureLoader
#from ..graphics import TextureArray, TextureHandle, TextureData
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

"""
class _TextureManager(Static):
	__TextureHandles = {}
	__TextureArrays = []
	__LastId = 0
	BlankArray = -1
	FontArray = -1

	def Reload() -> None:
		TextureArray.UnbindAll()
		for arr in TextureManager.__TextureArrays:
			ObjectManager.DeleteObject(arr)
		
		TextureManager.__TextureHandles.clear()
		TextureManager.__TextureArrays.clear()
		TextureManager.__LastId = 0
		TextureManager.BlankArray = -1
		TextureManager.FontArray = -1

		TextureManager.GetArray.cache_clear()
		TextureManager.GetTexture.cache_clear()

	def CreateBlankArray() -> None:
		if TextureManager.BlankArray != -1:
			Log("Blank texture array already created.", LogLevel.Warning)
			return
		
		ta = TextureArray(1, 1, 1, 1, TextureMagFilter.Nearest, isBlank = True)
		TextureManager.__TextureArrays.append(ta)
		ta.UploadTexture(GetWhiteTexture())

		_id = TextureManager.__LastId
		TextureManager.__LastId += 1

		TextureManager.BlankArray = _id

	def CreateTextureArray(width: int, height: int, layers: int, levels: int = 2, magFilter: TextureMagFilter = TextureMagFilter.Linear, isBlank = False) -> int:
		TextureManager.__TextureArrays.append(TextureArray(width, height, layers, levels, magFilter, isBlank))

		_id = TextureManager.__LastId
		TextureManager.__LastId += 1

		return _id
	
	def DeleteArray(_id):
		del TextureManager.__TextureArrays[_id]

	def LoadTexture(filepath: str, texArrayId: int) -> TextureHandle:
		handle = TextureLoader.LoadTexture(filepath, TextureManager.GetArray(texArrayId), texArrayId)
		TextureManager.__TextureHandles[os.path.abspath(filepath)] = handle
	
	def UploadTexture(texData: TextureData, texArray: int) -> TextureHandle:
		return TextureManager.__TextureArrays[texArray].UploadTexture(texData)
	
	@lru_cache
	def GetArray(_id: int) -> TextureArray:
		return TextureManager.__TextureArrays[_id]
	
	@lru_cache
	def GetTexture(name: str) -> TextureHandle:
		return TextureManager.__TextureHandles[os.path.abspath(name)]
	
	def GetTextureNames() -> dict:
		return TextureManager.__TextureHandles
	
	def GetTextureArrays() -> list:
		return TextureManager.__TextureArrays
	
	def GetTextureHandles() -> list:
		return TextureManager.__TextureHandles.values()
"""