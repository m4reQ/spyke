from .enums import WindowAPI
from .events import WindowEvent
from .keys import Key, Keys, MouseButton
from .utils import Static

import pygame

class InputHandler(Static):
	Api = WindowAPI.NoAPI

	__Initialized = False

	__Events = []
	__Keys = []
	__MouseButtons = []

	MousePos = (0, 0)
	MouseScrollOffset = (0, 0)

	IsKeyDown = lambda _: None
	IsKeyUp = lambda _: None
	IsButtonDown = lambda _: None
	IsButtonUp = lambda _: None

	UpdateKeyState = lambda: None

	def Initialize(windowApi: WindowAPI) -> None:
		InputHandler.Api = windowApi

		if InputHandler.Api == WindowAPI.Pygame:
			InputHandler.IsKeyDown = InputHandler.__PygameIsKeyDown
			InputHandler.IsKeyUp = InputHandler.__PygameIsKeyUp
			InputHandler.IsButtonDown = InputHandler.__PygameIsButtonDown
			InputHandler.IsButtonUp = InputHandler.__PygameIsButtonUp

			InputHandler.UpdateKeyState = __PygameUpdateKeyState
		elif InputHandler.Api == WindowAPI.GLFW:
			InputHandler.IsKeyDown = InputHandler.__GlfwIsKeyDown
			InputHandler.IsKeyUp = InputHandler.__GlfwIsKeyUp
			InputHandler.IsButtonDown = InputHandler.__GlfwIsButtonDown
			InputHandler.IsButtonUp = InputHandler.__GlfwIsButtonUp

		InputHandler.Initialized = True
	
	def __PygameUpdateKeyState() -> None:
		InputHandler.__Keys = pygame.key.get_pressed()
	
	def PutEvent(event: WindowEvent) -> None:
		InputHandler.__Events.append(event)
	
	def GetEvent() -> WindowEvent or None:
		try:
			event = InputHandler.__Events[0]
		except IndexError:
			return None
		
		InputHandler.__Events.remove(event)
		return event
	
	def RemoveEvent(event: WindowEvent) -> None:
		try:
			InputHandler.__Events.remove(event)
		except ValueError:
			pass
	
	def GetEvents() -> list:
		return InputHandler.__Events
	
	def ClearEvents() -> None:
		InputHandler.__Events.clear()
	
	def ClearKeys() -> None:
		InputHandler.__Keys.clear()
		InputHandler.__MouseButtons.clear()

	def AddKey(key: int) -> None:
		InputHandler.__Keys.append(key)
	
	def AddButton(button: int) -> None:
		InputHandler.__MouseButtons.append(button)

	def Resized() -> bool:
		return WindowEvent.ResizeEvent in InputHandler.__Events
	
	def FileDropped() -> bool:
		return WindowEvent.FileDropEvent in InputHandler.__Events
	
	def TextDropped() -> bool:
		return WindowEvent.TextDropEvent in InputHandler.__Events
	
	def MouseMoved() -> bool:
		return WindowEvent.MouseMoveEvent in InputHandler.__Events
	
	def MouseScrolled() -> bool:
		return WindowEvent.MouseScrollEvent in InputHandler.__Events
	
	def KeyPressed() -> bool:
		return WindowEvent.KeyEvent in InputHandler.__Events
	
	def LastKeyPressed() -> Key or None:
		try:
			return InputHandler.__Keys[-1]
		except IndexError:
			return None
	
	def __PygameIsKeyDown(key: Key) -> bool:
		return key.Pygame in InputHandler.__Keys
	
	def __GlfwIsKeyDown(key: Key) -> bool:
		return key.Glfw in InputHandler.__Keys
	
	def __PygameIsKeyUp(key: Key) -> bool:
		return key.Pygame not in InputHandler.__Keys
	
	def __GlfwIsKeyUp(key: Key) -> bool:
		return key.Glfw not in InputHandler.__Keys

	def __PygameIsButtonDown(button: MouseButton) -> bool:
		return button.Pygame in InputHandler.__MouseButtons
	
	def __GlfwIsButtonDown(button: MouseButton) -> bool:
		return button.Glfw in InputHandler.__MouseButtons

	def __PygameIsButtonUp(button: MouseButton) -> bool:
		return button.Pygame not in InputHandler.__MouseButtons
	
	def __GlfwIsButtonUp(button: MouseButton) -> bool:
		return button.Glfw not in InputHandler.__MouseButtons