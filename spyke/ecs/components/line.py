from ...transform import Vector3

class LineComponent(object):
	def __init__(self, startPos: Vector3, endPos: Vector3):
		self.StartPos = startPos
		self.EndPos = endPos