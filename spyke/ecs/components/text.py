import glm

class TextComponent:
	__slots__ = (
		'__weakref__',
		'text',
		'size',
		'color',
		'font',
	)
	
	def __init__(self, text: str, size: int, font_name: str, color: glm.vec4):
		self.text: str = text
		self.size: int = size
		self.color: glm.vec4 = color
		self.font: str = font_name