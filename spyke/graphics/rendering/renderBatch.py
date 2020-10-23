from ...utils import GL_FLOAT_SIZE

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
	
	def TryAddData(self, data: list) -> bool:
		if self.dataSize + len(data) * GL_FLOAT_SIZE > self.maxSize:
			return False

		self.data.extend(data)
		self.dataSize += len(data) * GL_FLOAT_SIZE

		return True
	
	def Clear(self) -> None:
		self.data.clear()
		self.dataSize = 0
		self.indexCount = 0
	
	def WouldAccept(self, size) -> bool:
		return self.dataSize + size <= self.maxSize
	
	@property
	def IsAccepting(self) -> bool:
		return self.dataSize < self.maxSize