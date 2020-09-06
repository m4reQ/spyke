class Glyph(object):
	def __init__(self, x: float, y: float, width: int, height: int, texWidth: float, texHeight: float, bearingX: int, bearingY: int, advance: int):
		self.X = x
		self.Y = y
		self.Width = width
		self.Height = height
		self.TexWidth = texWidth
		self.TexHeight = texHeight
		self.BearingX = bearingX
		self.BearingY = bearingY
		self.Advance = advance