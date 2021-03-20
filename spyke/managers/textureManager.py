#region Import
from ..utils import Static
from ..debugging import Debug, LogLevel
from ..loaders.texture import LoadTexture
from ..graphics.texturing.texture import Texture
from ..graphics.texturing.textureSpec import TextureSpec
#endregion

class TextureManager(Static):
	Textures = {}

	def LoadTexture(filepath: str, tSpec: TextureSpec = TextureSpec()) -> Texture:
		if filepath in TextureManager.Textures.keys():
			Debug.Log("Texture already loaded.", LogLevel.Warning)
			return

		textureData = LoadTexture(filepath)
		tex = Texture(textureData, tSpec)
		TextureManager.Textures[filepath] = tex

		return tex
