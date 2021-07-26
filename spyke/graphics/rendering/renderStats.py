from ...autoslot import Slots

class RenderStats(Slots):
	__slots__ = ["__weakref__", ]

	def __init__(self):
		self.drawsCount = 0
		self.vertexCount = 0
		self.drawTime = 1.0
		self.videoMemoryUsed = 0.0
	
	def Clear(self):
		self.drawsCount = 0
		self.vertexCount = 0
		self.drawTime = 1.0
		self.videoMemoryUsed = 0.0