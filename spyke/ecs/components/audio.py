class AudioComponent:
	__slots__ = ('__weakref__', 'sound', 'ended', 'looping')
	
	def __init__(self, sound_name: str, looping: bool):
		self.sound = sound_name
		self.ended = False
		self.looping = looping