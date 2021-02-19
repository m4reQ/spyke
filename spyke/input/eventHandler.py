from ..utils.functional import Static

"""
Function prototypes:

ResizeCallback(width: int, height: int) -> bool
params:
* width - new display width
* height - new display height

KeyDownCallback(key: int, mods: int, repeated: bool) -> bool
params:
* key - keycode
* mods - modifier keys that was pressed when key press was registered
* repeated - indicates if key was already pressed when a callback got triggered

KeyUpCallback(key: int) -> bool
params:
* key - keycode

MouseButtonDownCallback(button: int) -> bool
params:
* button - button code

MouseButtonUpCallback(button: int) -> bool
params:
* button - button code

MouseMoveCallback(x: int, y: int) -> bool
params:
* x - new mouse x position
* y - new mouse y position

MouseScrollCallback(x: int, y: int) -> bool
params:
* x - x scroll offset (negative for down scroll, positive for up)
* y - y scroll offset (negative for left scroll, positive for right)

WindowMoveCallback(x: int, y: int) -> bool
params:
* x - new window X position
* y - new window Y position

WindowFocusCallback() -> bool

WindowLostFocusCallback() -> bool

WindowCloseCallback() -> bool
"""


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