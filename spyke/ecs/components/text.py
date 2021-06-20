from ...managers.fontManager import FontManager
from ...memory import Serializable
from ...utils import SecureSpaces, RestoreSpaces

import glm

class TextComponent(Serializable):
	ClassName = "TextComponent"
	
	@classmethod
	def Deserialize(cls, data):
		data = data.split(" ")

		col = glm.vec4(float(data[3]), float(data[4]), float(data[5]), float(data[6]))

		return cls(RestoreSpaces(data[0]), int(data[1]), data[2], col)

	def __init__(self, text: str, size: int, font: str, color: glm.vec4):
		self.text = text
		self.size = size
		self.font = FontManager.GetFont(font)
		self.fontName = font
		self.color = color
	
	def Serialize(self):
		s = f"{SecureSpaces(self.Text)} {self.Size} {self.FontName} "
		s += f"{self.Color.x} {self.Color.y} {self.Color.z} {self.Color.w}"

		return s