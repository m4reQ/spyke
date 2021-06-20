class EventHook(object):
	def __init__(self, func: callable, priority: int = 0):
		self.func = func
		self.priority = priority