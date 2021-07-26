from ...autoslot import Slots
import glm

class SpriteComponent(Slots):
	__slots__ = ("__weakref__", )
	
	def __init__(self, texName: str, tilingFactor: glm.vec2, color: glm.vec4):
		self.texture = texName
		self.tilingFactor = tilingFactor
		self.color = color