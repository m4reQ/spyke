from .glyph import Glyph
from .fontManager import FontManager
from ..texturing.textureLoader import LoadTexture
from ...debug import Log, LogLevel, Timer

class Font(object):
	@staticmethod
	def LoadFont(filepath: str, texSize: tuple):
		Timer.Start()
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
			data = [0] * 10

			data[0] = int(lineData[1][2:]) / texSize[0]
			data[1] = int(lineData[2][2:]) / texSize[1]
			data[2] = int(lineData[3][6:])
			data[3] = int(lineData[4][7:])
			data[4] = int(lineData[3][6:]) / texSize[0]
			data[5] = int(lineData[4][7:]) / texSize[1]
			data[6] = int(lineData[5][8:])
			data[7] = int(lineData[6][8:])
			data[8] = int(lineData[7][9:])
			data[9] = int(lineData[0][3:])

			characters[data[9]] = Glyph(*data)
		
		if None in characters:
			raise RuntimeError("Cannot generate font.")
			
		Log(f"Font generated in {Timer.Stop()} seconds.", LogLevel.Info)

		return (characters, base)

	def __init__(self, fontFilepath: str, bitmapFilepath: str):
		if not FontManager.Initialized:
			FontManager.Initialize()

		texData = LoadTexture(bitmapFilepath)

		self.__texId = FontManager.AddTexture(texData).Index
		self.characters, self.baseSize = Font.LoadFont(fontFilepath, (texData.Width, texData.Height))

	def GetGlyph(self, charId: int):
		try:
			return self.characters[charId]
		except KeyError:
			raise RuntimeError(f"Cannot find glyph with id: {charId}.")
	
	@property
	def TextureIndex(self):
		return self.__texId