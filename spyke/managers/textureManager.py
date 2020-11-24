#region Import
from ..utils import Static, Timer
from ..debug import Log, LogLevel
from ..textureLoader import TextureLoader
from ..graphics import TextureArray, TextureHandle, TextureData
from ..graphics.texturing.textureUtils import GetWhiteTexture, IMAGE_FORMAT_MAP
from ..enums import TextureMagFilter

import os
from functools import lru_cache
from PIL import Image
#endregion

class TextureManager(Static):
	__TextureHandles = {}
	__TextureArrays = []

	__LastId = 0
	BlankArray = -1

	__HasBlankArray = False

	def CreateBlankArray() -> None:
		if TextureManager.__HasBlankArray:
			Log("Blank texture array already created.", LogLevel.Warning)
			return
		
		ta = TextureArray(1, 1, 1, 1, TextureMagFilter.Nearest)
		TextureManager.__TextureArrays.append(ta)
		ta.UploadTexture(GetWhiteTexture())

		_id = TextureManager.__LastId
		TextureManager.__LastId += 1

		TextureManager.BlankArray = _id

	def CreateTextureArray(width: int, height: int, layers: int, levels: int = 2, magFilter: TextureMagFilter = TextureMagFilter.Linear) -> int:
		TextureManager.__TextureArrays.append(TextureArray(width, height, layers, levels, magFilter))

		_id = TextureManager.__LastId
		TextureManager.__LastId += 1

		return _id

	def LoadTexture(filepath: str, texArrayId: int) -> TextureHandle:
		handle = TextureLoader.LoadTexture(filepath, TextureManager.GetArray(texArrayId))
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
		return TextureManager.__TextureArrays.values()
	
	def GetTextureHandles() -> list:
		return TextureManager.__TextureHandles.values()