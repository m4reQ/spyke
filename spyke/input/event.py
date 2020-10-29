#region Import
from ..utils.functional import Enum, Abstract
from ..debug import Timer
#endregion

BIT = lambda x: 1 << x

class EventType(Enum):
	Default = 0
	WindowStart, WindowClose, WindowResize, WindowFocus, WindowLostFocus, WindowMoved = range(1, 7)
	KeyPressed, KeyReleased = range(7, 9)
	MouseButtonPressed, MouseButtonReleased, MouseMoved, MouseScrolled = range(9, 13)

class EventCategory(Enum):
	Default 			= 0
	CategoryInput 		= BIT(0)
	CategoryWindow 		= BIT(1)
	CategoryKeyboard 	= BIT(2)
	CategoryMouse 		= BIT(3)
	CategoryMouseButton = BIT(4)

class Event(Abstract):
	def __init__(self, eventType: EventType, category: EventCategory):
		self.Handled = False
		self.Type = eventType
		self.Category = category
	
	def IsInCategory(self, category: EventCategory):
		return self.Category & category

#region WindowEvents
class WindowResizeEvent(Event):
	def __init__(self, width: int, height: int):
		super().__init__(EventType.WindowResize, EventCategory.CategoryWindow)
		self.Width = width
		self.Height = height

class WindowStartEvent(Event):
	def __init__(self):
		super().__init__(EventType.WindowStart, EventCategory.CategoryWindow)

		self.Time = Timer.GetCurrent()

class WindowCloseEvent(Event):
	def __init__(self):
		super().__init__(EventType.WindowClose, EventCategory.CategoryWindow)

		self.Time = Timer.GetCurrent()

class WindowFocusEvent(Event):
	def __init__(self):
		super().__init__(EventType.WindowFocus, EventCategory.CategoryWindow)

class WindowLostFocusEvent(Event):
	def __init__(self):
		super().__init__(EventType.WindowLostFocus, EventCategory.CategoryWindow)

class WindowMovedEvent(Event):
	def __init__(self, posX: int, posY: int):
		super().__init__(EventType.WindowMoved, EventCategory.CategoryWindow)
		self.X = posX
		self.Y = posY
		self.Position = (posX, posY)
#endregion
#region KeyEvents
class KeyPressedEvent(Event):
	def __init__(self, keyCode: int, repeatCount: int):
		super().__init__(EventType.KeyPressed, EventCategory.CategoryKeyboard | EventCategory.CategoryInput)
		self.KeyCode = keyCode
		self.RepeatCount = repeatCount
	
	@property
	def IsRepeated(self) -> int:
		return self.RepeatCount

class KeyReleasedEvent(Event):
	def __init__(self, keyCode: int):
		super().__init__(EventType.KeyReleased, EventCategory.CategoryKeyboard | EventCategory.CategoryInput)
		self.KeyCode = keyCode
#endregion
#region MouseEvents
class MouseButtonPressedEvent(Event):
	def __init__(self, button: int):
		super().__init__(EventType.MouseButtonPressed, EventCategory.CategoryMouse | EventCategory.CategoryMouseButton | EventCategory.CategoryInput)

class MouseButtonReleasedEvent(Event):
	def __init__(self, button: int):
		super().__init__(EventType.MouseButtonReleased, EventCategory.CategoryMouse | EventCategory.CategoryMouseButton | EventCategory.CategoryInput)

class MouseMovedEvent(Event):
	def __init__(self, posX: int, posY: int):
		super().__init__(EventType.MouseMoved, EventCategory.CategoryMouse | EventCategory.CategoryInput)
		self.X = posX
		self.Y = posY
		self.Position = (posX, posY)

class MouseScrolledEvent(Event):
	def __init__(self, xOffset: int, yOffset: int):
		super().__init__(EventType.MouseScrolled, EventCategory.CategoryMouse | EventCategory.CategoryInput)
		self.OffsetX = xOffset
		self.OffsetY = yOffset
#endregion