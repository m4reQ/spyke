from ...utils import Serializable

import glm

class LineComponent(Serializable):
	ClassName = "LineComponent"
	
	@classmethod
	def Deserialize(cls, data):
		data = data.split(" ")
		data = [float(x) for x in data]

		start = glm.vec3(data[0], data[1], data[2])
		end = glm.vec3(data[3], data[4], data[5])
		col = glm.vec4(data[6], data[7], data[8], data[9])

		return cls(start, end, col)

	def __init__(self, startPos: glm.vec3, endPos: glm.vec3, color: glm.vec4):
		self.StartPos = startPos
		self.EndPos = endPos
		self.Color = color
	
	def Serialize(self):
		s = f"{self.StartPos.x} {self.StartPos.y} {self.StartPos.z} "
		s += f"{self.EndPos.x} {self.EndPos.y} {self.EndPos.z} "
		s += f"{self.Color.x} {self.Color.y} {self.Color.z} {self.Color.w}"

		return s