from ...autoslot import WeakSlots
import glm

class SpriteComponent(WeakSlots):
	def __init__(self, texName: str, tilingFactor: glm.vec2, color: glm.vec4):
		self.texture = texName
		self.tilingFactor = tilingFactor
		self.color = color