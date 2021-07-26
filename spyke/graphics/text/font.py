from .glyph import Glyph
from ...autoslot import Slots

from functools import lru_cache

INVALID_GLYPH_ID = 0

class Font(Slots):
	__slots__ = ("__weakref__", )
	
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