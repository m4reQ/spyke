from ...utils import SecureSpaces, RestoreSpaces
from ...memory import Serializable

class TagComponent(Serializable):
	@classmethod
	def Deserialize(cls, data):
		data = data.split(" ")

		return cls(RestoreSpaces(data[0]))

	def __init__(self, name):
		self.Name = name
	
	def Serialize(self):
		return f"{SecureSpaces(self.Name)}"