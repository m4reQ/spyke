from ...autoslot import WeakSlots
import glm

class TextComponent(WeakSlots):
	def __init__(self, text: str, size: int, fontName: str, color: glm.vec4):
		self.text = text
		self.size = size
		self.color = color
		self.font = fontName