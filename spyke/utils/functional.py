class Iterator(object):
	def __init__(self, iterable, looping: bool = False):
		self.iterable = iterable
		self.lastPos = 0
		self.looping = looping

	def __next__(self):
		pos = self.lastPos
		self.lastPos += 1

		if self.lastPos >= len(self.iterable):
			if self.looping:
				self.lastPos = 0
			else:
				raise StopIteration

		return self.iterable[pos]