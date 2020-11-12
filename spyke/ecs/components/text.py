from ...graphics import Font

class TextComponent(object):
	def __init__(self, text: str, size: int, font: Font):
		self.Text = text
		self.Size = size
		self.Font = font