#region Import
from .textureManager import TextureManager
from ..graphics import TextureArray, TextureData, TextureHandle
from ..graphics.text.font import Font
from ..debug import Log, LogLevel
from ..enums import TextureMagFilter
from ..utils import Static
from ..textureLoader import TextureLoader

from functools import lru_cache
#endregion

class FontManager(Static):
	__TextureWidth = 512
	__TextureHeight = 512
	__MaxFontTextures = 5

	__Fonts = {}

	def Reload() -> None:
		FontManager.__Fonts.clear()
	
	def Use() -> None:
		TextureManager.GetArray(TextureManager.FontArray).Bind()
	
	def CreateFont(fontFilepath: str, bitmapFilepath: str, fontName: str) -> None:
		if TextureManager.FontArray == -1:
			TextureManager.FontArray = TextureManager.CreateTextureArray(FontManager.__TextureWidth, FontManager.__TextureHeight, FontManager.__MaxFontTextures, 1)

		TextureManager.LoadTexture(bitmapFilepath, TextureManager.FontArray)
		FontManager.__Fonts[fontName] = Font(fontFilepath, bitmapFilepath)
	
	@lru_cache
	def GetFont(fontName: str) -> Font:
		return FontManager.__Fonts[fontName]

	def GetFonts() -> dict:
		return FontManager.__Fonts