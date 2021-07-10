import glm

class SpriteComponent(object):
	__slots__ = ("texture", "tilingFactor", "color")
	
	def __init__(self, texName: str, tilingFactor: glm.vec2, color: glm.vec4):
		self.texture = texName
		self.tilingFactor = tilingFactor
		self.color = color