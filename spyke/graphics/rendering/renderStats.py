class RenderStats(object):
	def __init__(self):
		self.VertexCount = 0
		self.DrawsCount = 0
		self.DrawTime = 0.0
	
	def Clear(self):
		self.VertexCount = 0
		self.DrawsCount = 0
		self.DrawTime = 0.0