class RenderStats:
	quadsCount = 0
	drawsCount = 0
	vertexCount = 0
	frameEnded = False
	
	@staticmethod
	def Clear():
		RenderStats.quadsCount = 0
		RenderStats.drawsCount = 0
		RenderStats.vertexCount = 0
		RenderStats.frameEnded = False