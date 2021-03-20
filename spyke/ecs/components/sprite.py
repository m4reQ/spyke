from ...managers.textureManager import TextureManager
from ...memory import Serializable

import glm

class SpriteComponent(Serializable):
	ClassName = "SpriteComponent"
	
	@classmethod
	def Deserialize(cls, data):
		data = data.split(" ")

		tf = glm.vec2(float(data[1]), float(data[2]))
		col = glm.vec4(float(data[3]), float(data[4]), float(data[5]), float(data[6]))

		return cls(data[0], tf, col)

	def __init__(self, texFilepath: str, tilingFactor: glm.vec2, color: glm.vec4):
		if not texFilepath:
			self.Texture = None
		else:
			try:
				self.Texture = TextureManager.Textures[texFilepath]
			except KeyError:
				TextureManager.LoadTexture(texFilepath)
				self.Texture = TextureManager.Textures[texFilepath]

		self.TextureName = texFilepath
		self.TilingFactor = tilingFactor
		self.Color = color
	
	def Serialize(self):
		s = f"{self.TextureName} "
		s += f"{self.TilingFactor.x} {self.TilingFactor.y} "
		s += f"{round(self.Color.x, 3)} {round(self.Color.y, 3)} {round(self.Color.z, 3)} {round(self.Color.w, 3)}"

		return s