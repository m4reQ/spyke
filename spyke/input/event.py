from .eventHook import EventHook

class Event(object):
	def __init__(self):
		self._hooks = []
	
	def AddHook(self, hook: EventHook):
		if hook in self._hooks:
			return

		if not self.__IsValidHook(hook):
			raise ValueError("Invalid event hook provided.")
		
		hook = self.__ParseHook(hook)

		self._hooks.append(hook)
		self._hooks.sort(key=lambda x: x.priority)
	
	def RemoveHook(self, hook: EventHook):
		if hook not in self._hooks:
			return
			
		if not self.__IsValidHook(hook):
			raise ValueError("Invalid event hook provided.")
		
		hook = self.__ParseHook(hook)

		if not hook in self._hooks:
			raise KeyError("Cannot found event hook.")

		self._hooks.remove(hook)
	
	def Invoke(self, *args, **kwargs):
		for hook in self._hooks:
			if hook.func(*args, **kwargs):
				break
	
	def __iadd__(self, hook: EventHook):
		self.AddHook(hook)
		return self
	
	def __isub__(self, hook: EventHook):
		self.RemoveHook(hook)
		return self
	
	def __IsValidHook(self, hook):
		if isinstance(hook, EventHook):
			return True
		elif isinstance(hook, tuple):
			if len(hook) != 2:
				return False
			return True
		else:
			return False
	
	def __ParseHook(self, hook):
		if isinstance(hook, EventHook):
			return EventHook(hook.func, hook.priority)
		elif isinstance(hook, tuple):
			return EventHook(hook[0], 0)