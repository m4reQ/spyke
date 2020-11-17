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

	__FontNames = {}

	TextureArray = None
	Initialized = False

	def Initialize() -> None:
		if FontManager.Initialized:
			Log("Font manager already initialized.", LogLevel.Warning)
			return
		
		FontManager.TextureArray = TextureManager.CreateTextureArray(FontManager.__TextureWidth, FontManager.__TextureHeight, FontManager.__MaxFontTextures, 1)

		FontManager.Initialized = True
	
	def Use() -> None:
		TextureManager.GetArray(FontManager.TextureArray).Bind()
	
	def CreateFont(fontFilepath: str, bitmapFilepath: str, fontName: str) -> None:
		if not FontManager.Initialized:
			Log("Font manager not initialized. Initializing...", LogLevel.Warning)
			FontManager.Initialize()

		TextureManager.LoadTexture(bitmapFilepath, FontManager.TextureArray)
		FontManager.__FontNames[fontName] = Font(fontFilepath, bitmapFilepath)
	
	@lru_cache
	def GetFont(fontName: str) -> Font:
		return FontManager.__FontNames[fontName]
