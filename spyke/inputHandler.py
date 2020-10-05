from .enums import WindowAPI
from .events import WindowEvent
from .keys import Key, Keys, MouseButton
from .utils import Static

class InputHandler(Static):
	Api = WindowAPI.NoAPI

	__Initialized = False

	__Events = []
	__Keys = []
	__MouseButtons = []

	MousePos = (0, 0)
	MouseScrollOffset = (0, 0)

	def Initialize(windowApi: WindowAPI):
		InputHandler.Api = windowApi

		InputHandler.Initialized = True
	
	def UpdateKeyState():
		if InputHandler.Api == WindowAPI.Pygame:
			InputHandler.__Keys = pygame.key.get_pressed()
		else:
			raise NotImplementedError()
	
	def PutEvent(event: WindowEvent):
		InputHandler.__Events.append(event)
	
	def GetEvent():
		try:
			event = InputHandler.__Events[0]
		except IndexError:
			return None
		
		InputHandler.__Events.remove(event)
		return event
	
	def GetEvents():
		return InputHandler.__Events
	
	def ClearEvents():
		InputHandler.__Events.clear()
	
	def ClearKeys():
		InputHandler.__Keys.clear()
		InputHandler.__MouseButtons.clear()

	def AddKey(key: int):
		InputHandler.__Keys.append(key)
	
	def AddButton(button: int):
		InputHandler.__MouseButtons.append(button)

	def Resized():
		return WindowEvent.ResizeEvent in InputHandler.__Events
	
	def FileDropped():
		return WindowEvent.FileDropEvent in InputHandler.__Events
	
	def TextDropped():
		return WindowEvent.TextDropEvent in InputHandler.__Events
	
	def MouseMoved():
		return WindowEvent.MouseMoveEvent in InputHandler.__Events
	
	def MouseScrolled():
		return WindowEvent.MouseScrollEvent in InputHandler.__Events
	
	def KeyPressed():
		return WindowEvent.KeyEvent in InputHandler.__Events
	
	def LastKeyPressed():
		try:
			return InputHandler.__Keys[-1]
		except IndexError:
			return -1
	
	def IsKeyDown(key: Key):
		if InputHandler.Api == WindowAPI.Pygame:
			return key.Pygame in InputHandler.__Keys
		elif InputHandler.Api == WindowAPI.GLFW:
			return key.Glfw in InputHandler.__Keys
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	def IsKeyUp(key: Key):
		if InputHandler.Api == WindowAPI.Pygame:
			return key.Pygame not in InputHandler.__Keys
		elif InputHandler.Api == WindowAPI.GLFW:
			return key.Glfw not in InputHandler.__Keys
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	def IsButtonDown(button: MouseButton):
		if InputHandler.Api == WindowAPI.Pygame:
			return button.Pygame in InputHandler.__MouseButtons
		elif InputHandler.Api == WindowAPI.GLFW:
			return button.Glfw in InputHandler.__MouseButtons
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	def IsButtonUp(button: MouseButton):
		if InputHandler.Api == WindowAPI.Pygame:
			return button.Pygame not in InputHandler.__MouseButtons
		elif InputHandler.Api == WindowAPI.GLFW:
			return button.Glfw not in InputHandler.__MouseButtons
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")