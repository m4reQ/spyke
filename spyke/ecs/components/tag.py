from ...autoslot import WeakSlots

class TagComponent(WeakSlots):
	def __init__(self, name):
		self.name = name