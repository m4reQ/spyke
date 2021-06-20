from enum import Enum

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

from .event import Event

class _EventHandler:
	def __init__(self):
		self.KeyDown = Event()
		self.KeyUp = Event()
		self.WindowClose = Event()
		self.WindowResize = Event()
		self.WindowMove = Event()
		self.MouseButtonUp = Event()
		self.MouseButtonDown = Event()
		self.MouseMove = Event()
		self.MouseScroll = Event()
		self.WindowFocus = Event()
		self.WindowLostFocus = Event()

EventHandler = _EventHandler()