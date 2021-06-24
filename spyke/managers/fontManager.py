#region Import
from .textureManager import TextureManager
from ..graphics.texturing.texture import TextureSpec
from ..graphics.text.font import Font

from functools import lru_cache
from OpenGL import GL
#endregion

class FontManager:
	__Fonts = {}
	
	def CreateFont(fontFilepath: str, imageFilepath: str, fontName: str) -> None:
		tSpec = TextureSpec()
		tSpec.minFilter = GL.GL_NEAREST
		tSpec.magFilter = GL.GL_NEAREST
		tSpec.mipmaps = 1
		tSpec.wrapMode = GL.GL_CLAMP_TO_EDGE
		tSpec.compress = False

		texture = TextureManager.LoadTexture(imageFilepath, tSpec)
		font = Font(fontFilepath, texture)
		font.ImageFilepath = imageFilepath

		FontManager.__Fonts[fontName] = font

		FontManager.GetFont.cache_clear()
	
	@lru_cache
	def GetFont(fontName: str) -> Font:
		return FontManager.__Fonts[fontName]

	def GetFonts() -> dict:
		return FontManager.__Fonts