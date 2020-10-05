from .utils import Enum

class WindowEvent(Enum):
	CloseEvent = 0
	ResizeEvent = 1
	MouseMoveEvent = 2
	MouseClickEvent = 3
	MouseScrollEvent = 4
	KeyEvent = 5
	IconifiedEvent = 6
	FileDropEvent = 7
	TextDropEvent = 8