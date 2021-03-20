import pickle

class Serializable(object):
	ClassName = "Serializable"

	@classmethod
	def Deserialize(cls, data: str) -> object:
		pass

	@classmethod
	def DeserializeBin(cls, data: bytes) -> object:
		return pickle.loads(data)
	
	def Serialize(self) -> str:
		pass

	def SerializeBin(self) -> bytes:
		return pickle.dumps(self)