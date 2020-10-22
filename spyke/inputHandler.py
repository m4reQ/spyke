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

	def Initialize(windowApi: WindowAPI) -> None:
		InputHandler.Api = windowApi

		InputHandler.Initialized = True
	
	def UpdateKeyState() -> None:
		if InputHandler.Api == WindowAPI.Pygame:
			InputHandler.__Keys = pygame.key.get_pressed()
		else:
			raise NotImplementedError()
	
	def PutEvent(event: WindowEvent) -> None:
		InputHandler.__Events.append(event)
	
	def GetEvent() -> WindowEvent or None:
		try:
			event = InputHandler.__Events[0]
		except IndexError:
			return None
		
		InputHandler.__Events.remove(event)
		return event
	
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
	
	def IsKeyDown(key: Key) -> bool:
		if InputHandler.Api == WindowAPI.Pygame:
			return key.Pygame in InputHandler.__Keys
		elif InputHandler.Api == WindowAPI.GLFW:
			return key.Glfw in InputHandler.__Keys
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	def IsKeyUp(key: Key) -> bool:
		if InputHandler.Api == WindowAPI.Pygame:
			return key.Pygame not in InputHandler.__Keys
		elif InputHandler.Api == WindowAPI.GLFW:
			return key.Glfw not in InputHandler.__Keys
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	def IsButtonDown(button: MouseButton) -> bool:
		if InputHandler.Api == WindowAPI.Pygame:
			return button.Pygame in InputHandler.__MouseButtons
		elif InputHandler.Api == WindowAPI.GLFW:
			return button.Glfw in InputHandler.__MouseButtons
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")
	
	def IsButtonUp(button: MouseButton) -> bool:
		if InputHandler.Api == WindowAPI.Pygame:
			return button.Pygame not in InputHandler.__MouseButtons
		elif InputHandler.Api == WindowAPI.GLFW:
			return button.Glfw not in InputHandler.__MouseButtons
		else:
			raise RuntimeError(f"Unsupported API: {InputHandler.Api}")