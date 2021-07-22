from ...autoslot import WeakSlots

class AudioComponent(WeakSlots):
	def __init__(self, soundName: str, looping: bool):
		self.sound = soundName
		self.ended = False
		self.looping = looping