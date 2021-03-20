from ...utils import StaticProperty

class RenderStats:
	QuadsCount = 0
	DrawsCount = 0
	VertexCount = 0
	DrawTime = 0.0
	FrameEnded = False
	
	@staticmethod
	def Clear():
		RenderStats.QuadsCount = 0
		RenderStats.DrawsCount = 0
		RenderStats.VertexCount = 0
		RenderStats.DrawTime = 0.0
		RenderStats.FrameEnded = False