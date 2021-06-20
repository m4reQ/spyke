class AudioComponent(object):
	def __init__(self, filepath: str, looping: bool):
		self.filepath = filepath
		self.handle = Sound(filepath)
		self.ended = False
		self.looping = looping