from ...graphics import Font
from ...managers.fontManager import FontManager

class TextComponent(object):
	def __init__(self, text: str, size: int, font: str):
		self.Text = text
		self.Size = size
		self.Font = FontManager.GetFont(font)
		self.FontName = font