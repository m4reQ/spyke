import glm

class SpriteComponent:
	__slots__ = (
		'__weakref__',
		'texture',
		'tiling_factor',
		'color'
	)
	
	def __init__(self, texture_name: str, tiling_factor: glm.vec2, color: glm.vec4):
		self.texture: str = texture_name
		self.tiling_factor: glm.vec2 = tiling_factor
		self.color: glm.vec4 = color