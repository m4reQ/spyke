#region Import
from .glyph import Glyph
from ..rectangle import RectangleF
from ...debugging import Debug, LogLevel
from ...exceptions import NovaException
from ..texturing.texture import Texture

from functools import lru_cache
import time
#endregion

class Font(object):
	@staticmethod
	def __LoadFont(filepath: str, texSize: tuple) -> list:
		start = time.perf_counter()

		characters = {}
		base = 1

		f = open(filepath, mode="r")
		lines = f.readlines()
		f.close()

		for line in lines:
			if not line.startswith("char "):
				idx = line.find("base=")
				if idx != -1:
					base = line[idx:].split(' ')[0]
					base = int(base.split('=')[-1])

				continue
			
			lineData = line[5:len(line) - 20]
			lineData = lineData.split(' ')
			lineData = [e for e in lineData if e != '' and e != ' ']

			width = int(lineData[3][6:])
			height = int(lineData[4][7:])
			bearX = int(lineData[5][8:])
			bearY = int(lineData[6][8:])
			adv = int(lineData[7][9:])
			_ord = int(lineData[0][3:])

			texX = int(lineData[1][2:]) / texSize[0]
			texY = int(lineData[2][2:]) / texSize[1]
			texWidth = int(lineData[3][6:]) / texSize[0]
			texHeight = int(lineData[4][7:]) / texSize[1]
			texRect = RectangleF(texX, texY, texWidth, texHeight)

			characters[_ord] = Glyph(width, height, bearX, bearY, adv, texRect, _ord)
		
		if None in characters: #?????????
			raise RuntimeError("Cannot generate font.")
			
		Debug.Log(f"Font generated in {time.perf_counter() - start} seconds.", LogLevel.Info)

		return (characters, base)

	def __init__(self, fontFilepath: str, texture: Texture):
		self.FontFilepath = fontFilepath
		self.ImageFilepath = ""

		self.characters, self.baseSize = Font.__LoadFont(fontFilepath, (texture.width, texture.height))
		self.texture = texture

	@lru_cache
	def GetGlyph(self, charId: int) -> Glyph:
		try:
			return self.characters[charId]
		except KeyError:
			raise NovaException(f"Cannot find glyph with id: {charId}.")