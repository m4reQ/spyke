from ...autoslot import Slots

class TagComponent(Slots):
	__slots__ = ("__weakref__", )
	
	def __init__(self, name):
		self.name = name