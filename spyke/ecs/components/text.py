from ...autoslot import Slots
import glm

class TextComponent(Slots):
	__slots__ = ("__weakref__", )
	
	def __init__(self, text: str, size: int, fontName: str, color: glm.vec4):
		self.text = text
		self.size = size
		self.color = color
		self.font = fontName