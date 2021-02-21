#region Import
from ..utils import Static
from ..debugging import Log, LogLevel
from ..loaders.texture import LoadTexture
from ..graphics.texturing.texture import Texture
#endregion

class TextureManager(Static):
	Textures = {}

	def LoadTexture(filepath: str,):
		if filepath in TextureManager.Textures.keys():
			Log("Texture already loaded.", LogLevel.Warning)
			return

		textureData = LoadTexture(filepath)
		TextureManager.Textures[filepath] = Texture(textureData)