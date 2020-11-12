from ...graphics import TextureHandle

class SpriteComponent(object):
	def __init__(self, textureHandle: TextureHandle, tilingFactor: tuple):
		self.TextureHandle = textureHandle
		self.TilingFactor = tilingFactor