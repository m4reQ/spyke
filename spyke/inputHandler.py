from .windowUtils import WindowAPI
from .events import WindowEvent
from .keys import Key, Keys, MouseButton
import pygame

class InputHandler(object):
	Api = WindowAPI.NoAPI

	__Initialized = False

	__Events = []
	__Keys = []
	__MouseButtons = []

	MousePos = (0, 0)
	MouseScrollOffset = (0, 0)

	@staticmethod
	def Initialize(windowApi: WindowAPI):
		InputHandler.Api = windowApi

		InputHandler.Initialized = True
	
	@staticmethod
	def UpdateKeyState():
		if InputHandler.Api == WindowAPI.Pygame:
			InputHandler.__Keys = pygame.key.get_pressed()
		else:
			raise NotImplementedError()
	
	@staticmethod
	def PutEvent(event: WindowEvent):
		InputHandler.__Events.append(event)
	
	@staticmethod
	def GetEvent():
		try:
			event = InputHandler.__Events[0]
		except IndexError:
			return None
		
		InputHandler.__Events.remove(event)
		return event
	
	@staticmethod
	def GetEvents():
		return InputHandler.__Events
	
	@staticmethod
	def ClearEvents():
		InputHandler.__Events.clear()
	
	@staticmethod
	def ClearKeys():
		InputHandler.__Keys.clear()
		InputHandler.__MouseButtons.clear()

	@staticmethod
	def AddKey(key: int):
		InputHandler.__Keys.append(key)
	
	@staticmethod
	def AddButton(button: int):
		InputHandler.__MouseButtons.append(button)

	@staticmethod
	def Resized():
		return WindowEvent.ResizeEvent in InputHandler.__Events
	
	@staticmethod
	def FileDropped():
		return WindowEvent.FileDropEvent in InputHandler.__Events
	
	@staticmethod
	def TextDropped():
		return WindowEvent.TextDropEvent in InputHandler.__Events
	
	@staticmethod
	def MouseMoved():
		return WindowEvent.MouseMoveEvent in InputHandler.__Events
	
	@staticmethod
	def MouseScrolled():
		return WindowEvent.MouseScrollEvent in InputHandler.__Events
	
	@staticmethod
	def KeyPressed():
		return WindowEvent.KeyEvent in InputHandler.__Events
	
	@staticmethod
	def LastKeyPressed():
		try:
			return InputHandler.__Keys[-1]
		except IndexError:
			return -1
	
	@staticmethod
	def IsKeyDown(key: Key):
		if InputHandler.Api == WindowAPI.Pygame:
			return key.Pygame in InputHandler.__Keys
		elif InputHandler.Api == WindowAPI.GLFW:
			return key.Glfw in InputHandler.__Keys
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	@staticmethod
	def IsKeyUp(key: Key):
		if InputHandler.Api == WindowAPI.Pygame:
			return key.Pygame not in InputHandler.__Keys
		elif InputHandler.Api == WindowAPI.GLFW:
			return key.Glfw not in InputHandler.__Keys
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	@staticmethod
	def IsButtonDown(button: MouseButton):
		if InputHandler.Api == WindowAPI.Pygame:
			return button.Pygame in InputHandler.__MouseButtons
		elif InputHandler.Api == WindowAPI.GLFW:
			return button.Glfw in InputHandler.__MouseButtons
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	@staticmethod
	def IsButtonUp(button: MouseButton):
		if InputHandler.Api == WindowAPI.Pygame:
			return button.Pygame not in InputHandler.__MouseButtons
		elif InputHandler.Api == WindowAPI.GLFW:
			return button.Glfw not in InputHandler.__MouseButtons
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")