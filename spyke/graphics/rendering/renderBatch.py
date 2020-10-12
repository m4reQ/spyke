from ....utils import GL_FLOAT_SIZE

class RenderBatch(object):
	def __init__(self, maxSize: int):
		self.maxSize = maxSize
		self.texarrayID = -1
		self.data = []
		self.dataSize = 0
		self.indexCount = 0
	
	def AddData(self, data: list) -> None:
		if self.dataSize + len(data) * GL_FLOAT_SIZE > self.maxSize:
			raise RuntimeError("Cannot store more data in render batch.")

		self.data.extend(data)
		self.dataSize += len(data) * GL_FLOAT_SIZE
	
	def Clear(self) -> None:
		self.data.clear()
		self.dataSize = 0
		self.indexCount = 0
	
	@property
	def IsAccepting(self) -> bool:
		return self.dataSize < self.maxSize