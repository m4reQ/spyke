#region Import
from ..graphics.texturing.textureArray import TextureArray, TexArraySpec
from ..graphics.text.font import Font
from ..graphics.rendering.rendererSettings import RendererSettings
from ..loaders.texture import LoadTexture
from ..debug import Log, LogLevel
from ..utils import Static

from functools import lru_cache
from OpenGL import GL
#endregion

class FontManager(Static):
	__TextureWidth = 512
	__TextureHeight = 512

	__Fonts = {}

	__TextureArray = None

	def Initialize():
		if not FontManager.__TextureArray:
			spec = TexArraySpec(FontManager.__TextureWidth, FontManager.__TextureHeight, RendererSettings.MaxFontTextures)
			spec.minFilter = GL.GL_NEAREST_MIPMAP_NEAREST
			spec.magFilter = GL.GL_NEAREST
			spec.mipLevels = 1

			FontManager.__TextureArray = TextureArray(spec)
		else:
			Log("Font manager already intialized.", LogLevel.Warning)

	def Reload() -> None:
		FontManager.__Fonts.clear()
	
	def Use() -> None:
		FontManager.__TextureArray.Bind()
	
	def CreateFont(fontFilepath: str, imageFilepath: str, fontName: str) -> None:
		if not FontManager.__TextureArray:
			FontManager.Initialize()
		
		data = LoadTexture(imageFilepath)
		handle = FontManager.__TextureArray.UploadTexture(data)

		FontManager.__Fonts[fontName] = Font(fontFilepath, handle)
		FontManager.__Fonts[fontName].ImageFilepath = imageFilepath

		FontManager.GetFont.cache_clear()
	
	@lru_cache
	def GetFont(fontName: str) -> Font:
		return FontManager.__Fonts[fontName]

	def GetFonts() -> dict:
		return FontManager.__Fonts