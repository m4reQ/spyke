from ..utils.functional import Static

class EventType:
	KeyDown, KeyUp, WindowClose, WindowResize, WindowMove, MouseButtonUp, MouseButtonDown, MouseMove, MouseScroll, WindowFocus, WindowLostFocus = range(11)

class EventHook(object):
	def __init__(self, func: callable, priority: int = 0):
		self.__func = func
		self.priority = priority
	
	def Call(self, *args, **kwargs):
		self.__func(*args, **kwargs)

class EventHandler(Static):
	__Hooks = {}

	def PostEvent(_type: EventType, *args, **kwargs):
		try:
			for hook in EventHandler.__Hooks[_type]:
				if hook.Call(*args, **kwargs):
					break
		except KeyError:
			pass
	
	def BindHook(hook: EventHook, _type: EventType):
		try:
			EventHandler.__Hooks[_type].append(hook)
		except KeyError:
			EventHandler.__Hooks[_type] = [hook]
		
		EventHandler.__Hooks[_type].sort(key = lambda x: x.priority)
	
	def RemoveHook(hook: EventHook):
		for hookSet in EventHandler.__Hooks.values():
			try:
				hookSet.remove(hook)
			except ValueError:
				pass