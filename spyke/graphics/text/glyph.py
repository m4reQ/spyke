from ..rectangle import RectangleF

class Glyph(object):
	def __init__(self, width: int, height: int, bearingX: int, bearingY: int, advance: int, texRect: RectangleF, _ord: int):
		self.texRect = texRect
		self.width = width
		self.height = height
		self.bearingX = bearingX
		self.bearingY = bearingY
		self.advance = advance

		self.__ord = _ord
	
	def __repr__(self):
		return chr(self.__ord)