import glm

class LineComponent(object):
	def __init__(self, startPos: glm.vec3, endPos: glm.vec3, color: glm.vec4):
		self.StartPos = startPos
		self.EndPos = endPos
		self.Color = color