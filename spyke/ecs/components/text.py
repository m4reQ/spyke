import glm

class TextComponent(object):
	__slots__ = ("text", "size", "color", "font")

	def __init__(self, text: str, size: int, fontName: str, color: glm.vec4):
		self.text = text
		self.size = size
		self.color = color
		self.font = fontName