from .glyph import Glyph

from functools import lru_cache

INVALID_GLYPH_ID = 0

class Font(object):
	__slots__ = ("fontFilepath", "imageFilepath", "characters", "baseSize", "texture", "name")

	def __init__(self):
		self.fontFilepath = ""
		self.imageFilepath = ""
		self.name = ""
		self.characters = {}
		self.baseSize = 0
		self.texture = None

	@lru_cache
	def GetGlyph(self, charId: int) -> Glyph:
		if charId not in self.characters:
			return self.characters[INVALID_GLYPH_ID]
		else:
			return self.characters[charId]