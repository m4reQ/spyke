#region Import
from ..utils import Static, Timer, ObjectManager
from ..debug import Log, LogLevel
from ..loaders.texture import LoadTexture
from ..graphics.texturing.texture import Texture, TextureData
#endregion

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