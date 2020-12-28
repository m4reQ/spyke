from ...managers.textureManager import TextureManager

import glm

class SpriteComponent(object):
	def __init__(self, textureName: str, tilingFactor: glm.vec2, color: glm.vec4):
		self.TextureHandle = TextureManager.GetTexture(textureName)
		self.TextureName = textureName
		self.TilingFactor = tilingFactor
		self.Color = color