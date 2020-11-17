from ...graphics import TextureHandle
from ...managers import TextureManager

class SpriteComponent(object):
	def __init__(self, textureName: str, tilingFactor: tuple):
		self.TextureHandle = TextureManager.GetTexture(textureName)
		self.TilingFactor = tilingFactor