class AudioComponent(object):
	def __init__(self, filepath: str, looping: bool):
		self.Filepath = filepath
		self.Handle = Sound(filepath)
		self.Ended = False
		self.Looping = looping