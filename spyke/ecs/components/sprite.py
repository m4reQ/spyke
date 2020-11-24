from ...graphics import TextureHandle
from ...managers.textureManager import TextureManager

class SpriteComponent(object):
	def __init__(self, textureName: str, tilingFactor: tuple):
		self.TextureHandle = TextureManager.GetTexture(textureName)
		self.TextureName = textureName
		self.TilingFactor = tilingFactor