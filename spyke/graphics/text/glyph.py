class Glyph(object):
	def __init__(self, x: float, y: float, width: int, height: int, texWidth: float, texHeight: float, bearingX: int, bearingY: int, advance: int, _ord: int):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.texWidth = texWidth
		self.texHeight = texHeight
		self.bearingX = bearingX
		self.bearingY = bearingY
		self.advance = advance

		self.__ord = _ord
	
	def __repr__(self):
		return chr(self.__ord)