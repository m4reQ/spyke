from .textureArray import TextureArray
from .textureUtils import TextureData, GetWhiteTexture, TextureHandle
from .textureLoader import LoadTexture
from ...debug import Log, LogLevel
from ...utils import Static

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
		return TextureManager.__TextureArrays[texArray].UploadTexture(LoadTexture(filepath))