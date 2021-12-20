from abc import ABC
from typing import Tuple

class Event(ABC):
	def __init__(self):
		self.consumed = False

class KeyDownEvent(Event):
	def __init__(self, key: int, mods: int, repeat: bool):
		super().__init__()

		self.key = key
		self.mods = mods
		self.repeat = repeat

class KeyUpEvent(Event):
	def __init__(self, key: int):
		super().__init__()

		self.key = key

class ResizeEvent(Event):
	def __init__(self, width: int, height: int):
		super().__init__()

		self.width = width
		self.height = height
	
	@property
	def size(self) -> Tuple[int, int]:
		return (self.width, self.height)

class MouseButtonDownEvent(Event):
	def __init__(self, button: int):
		super().__init__()

		self.button = button

class MouseButtonUpEvent(Event):
	def __init__(self, button: int):
		super().__init__()

		self.button = button

class MouseMoveEvent(Event):
	def __init__(self, x: int, y: int):
		super().__init__()

		self.x = x
		self.y = y
	
	@property
	def position(self) -> Tuple[int, int]:
		return (self.x, self.y)

class MouseScrollEvent(Event):
	def __init__(self, x_offset: float, y_offset: float):
		super().__init__()

		self.x_offset = x_offset
		self.y_offset = y_offset

class WindowMoveEvent(Event):
	def __init__(self, x: int, y: int):
		super().__init__()

		self.x = x
		self.y = y
	
	@property
	def position(self) -> Tuple[int, int]:
		return (self.x, self.y)

class WindowFocusEvent(Event):
	pass

class WindowLostFocusEvent(Event):
	pass

class WindowCloseEvent(Event):
	pass