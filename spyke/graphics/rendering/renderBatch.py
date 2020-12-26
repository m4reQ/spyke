from ...utils import GL_FLOAT_SIZE

class RenderBatch(object):
	def __init__(self, maxSize: int):
		self.maxSize = maxSize
		self.data = []
		self.transformData = []
		self.texarrayID = -1
		self.indexCount = 0
	
	def AddTransformData(self, data: list) -> None:
		self.transformData.extend(data)

	def AddData(self, data: list) -> None:
		self.data.extend(data)
	
	def TryAddData(self, data: list) -> bool:
		if (len(self.data) + len(data)) * GL_FLOAT_SIZE > self.maxSize:
			return False

		self.data.extend(data)

		return True
	
	def Clear(self) -> None:
		self.data.clear()
		self.transformData.clear()
		self.indexCount = 0
	
	def WouldAccept(self, size) -> bool:
		return (len(self.data) * GL_FLOAT_SIZE) + size <= self.maxSize