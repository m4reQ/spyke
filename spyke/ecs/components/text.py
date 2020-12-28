from ...managers.fontManager import FontManager

import glm

class TextComponent(object):
	def __init__(self, text: str, size: int, font: str, color: glm.vec4):
		self.Text = text
		self.Size = size
		self.Font = FontManager.GetFont(font)
		self.FontName = font
		self.Color = color