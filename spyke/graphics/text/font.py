from spyke.graphics.texturing import Texture
from .glyph import Glyph
from typing import Dict
from functools import lru_cache

class Font:
	__slots__ = (
		'__weakref__',
		'font_filepath',
		'image_filepath',
		'name',
		'characters',
		'base_size',
		'texture'
	)
	
	def __init__(self):
		self.font_filepath: str = ""
		self.image_filepath: str = ""
		self.name: str = ""
		self.characters: Dict[int, Glyph] = {}
		self.base_size: int = 0
		self.texture: Texture = None

	@lru_cache
	def GetGlyph(self, char: str) -> Glyph:
		if char not in self.characters:
			return self.characters[chr(0)]
		else:
			return self.characters[char]