from ...utils import GL_FLOAT_SIZE

class RenderBatch(object):
	def __init__(self, maxSize: int):
		self.maxSize = maxSize
		self.data = []
		self.transformData = []
		self.indexCount = 0
		self.vertexCount = 0
	
	def Clear(self) -> None:
		self.data.clear()
		self.transformData.clear()
		self.indexCount = 0
		self.vertexCount = 0
	
	def WouldAccept(self, size) -> bool:
		return (len(self.data) * GL_FLOAT_SIZE) + size <= self.maxSize