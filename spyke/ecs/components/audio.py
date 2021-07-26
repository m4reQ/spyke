from ...autoslot import Slots

class AudioComponent(Slots):
	__slots__ = ("__weakref__", )
	
	def __init__(self, soundName: str, looping: bool):
		self.sound = soundName
		self.ended = False
		self.looping = looping