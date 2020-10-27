#region Import
from .textureArray import TextureArray
from .textureUtils import TextureData, GetWhiteTexture, TextureHandle, IMAGE_FORMAT_MAP
from ...debug import Log, LogLevel, Timer
from ...utils import Static

from functools import lru_cache
from PIL import Image
#endregion

class TextureLoader(Static):
	def LoadTexture(filepath: str) -> TextureData:
		Timer.Start()

		try:
			img = Image.open(filepath)
		except FileNotFoundError:
			raise RuntimeError(f"Cannot find image file: {filepath}.")

		texData = TextureData()
		texData.Width = img.size[0]
		texData.Height = img.size[1]

		texData.Data = list(img.getdata())
		texData.TextureType = IMAGE_FORMAT_MAP[img.mode]

		img.close()

		texData.ImageName = filepath

		Log(f"Image '{filepath}' loaded in {Timer.Stop()} seconds.", LogLevel.Info)

		return texData

class TextureManager(Static):
	__TextureArrays = []

	__LastId = 0

	__HasBlankArray = False
	BlankArray = -1

	def CreateBlankArray() -> None:
		if TextureManager.__HasBlankArray:
			Log("Blank texture array already created.", LogLevel)
		
		ta = TextureArray(1, 1, 1)
		TextureManager.__TextureArrays.append(ta)
		ta.UploadTexture(GetWhiteTexture())

		_id = TextureManager.__LastId
		TextureManager.__LastId += 1

		TextureManager.BlankArray = _id

	def CreateTextureArray(width: int, height: int, layers: int) -> int:
		TextureManager.__TextureArrays.append(TextureArray(width, height, layers))

		_id = TextureManager.__LastId
		TextureManager.__LastId += 1

		return _id
	
	def LoadTexture(filepath: str, texArray: int) -> TextureHandle:
		return TextureManager.UploadTexture(TextureLoader.LoadTexture(filepath), texArray)
	
	def UploadTexture(texData: TextureData, texArray: int) -> TextureHandle:
		return TextureManager.__TextureArrays[texArray].UploadTexture(texData)
	
	@lru_cache
	def GetArray(_id: int) -> TextureArray:
		return TextureManager.__TextureArrays[_id]