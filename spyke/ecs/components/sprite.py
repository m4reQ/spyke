from ...graphics import TextureHandle
from ...managers.textureManager import TextureManager

import glm

class SpriteComponent(object):
	def __init__(self, textureName: str, tilingFactor: glm.vec2):
		self.TextureHandle = TextureManager.GetTexture(textureName)
		self.TextureName = textureName
		self.TilingFactor = tilingFactor