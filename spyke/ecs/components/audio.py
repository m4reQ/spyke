class AudioComponent(object):
	__slots__ = ("hasEnded", "looping", "sound")
	
	def __init__(self, soundName: str, looping: bool):
		self.sound = soundName
		self.ended = False
		self.looping = looping