from .windowUtils import WindowAPI, WindowSpecs
from .debug import Log, LogLevel
from .inputHandler import InputHandler
from .events import WindowEvent

import pygame
from time import perf_counter

class PygameWindow(object):
	WindowCreationFlags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.OPENGL
	Api = WindowAPI.Pygame

	def __init__(self, specification: WindowSpecs):
		start = perf_counter()
		
		self.width = specification.Width
		self.height = specification.Height
		self.baseTitle = specification.Title

		self.specs = specification

		if not pygame.display.get_init():
			pygame.display.init()

		Log(f"Pygame version: {pygame.version.ver}", LogLevel.Info)

		pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, specification.GlVersionMajor)
		pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, specification.GlVersionMinor)
		pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)
		pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
		if specification.Multisample:
			pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, specification.Samples)

		flags = PygameWindow.WindowCreationFlags
		if specification.Fullscreen:
			flags |= pygame.FULLSCREEN
		else:
			if specification.Resizable:
				flags |= pygame.RESIZABLE
			
			if specification.Borderless:
				flags |= pygame.NOFRAME
		
		colorDepth = pygame.display.mode_ok((self.width, self.height), flags)

		self.__handle = pygame.display.set_mode((self.width, self.height), flags, colorDepth)

		pygame.display.set_caption(self.baseTitle)
		
		self.isRunning = True

		self.updateTime = 1.0
		self.renderTime = 1.0
		self.frameTime = 1.0

		Log(f"Pygame window initialized in {perf_counter() - start} seconds.", LogLevel.Info)

	def SwapBuffers(self):
		pygame.display.flip()

	def Update(self):
		pass

	def Render(self):
		pass

	def Close(self):
		pass

	def __DefUpdate(self):
		InputHandler.ClearEvents()
		InputHandler.ClearKeys()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.isRunning = False
				InputHandler.PutEvent(WindowEvent.CloseEvent)
			elif event.type == pygame.VIDEORESIZE:
				self.width = event.w
				self.height = event.h
				InputHandler.PutEvent(WindowEvent.ResizeEvent)
			elif event.type == pygame.KEYDOWN:
				InputHandler.PutEvent(WindowEvent.KeyEvent)
				InputHandler.AddKey(event.key)
			elif event.type == pygame.KEYUP:
				InputHandler.PutEvent(WindowEvent.KeyEvent)
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
				InputHandler.PutEvent(WindowEvent.MouseScrollEvent)
				InputHandler.MouseScrollOffset = (0, 1)
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
				InputHandler.PutEvent(WindowEvent.MouseScrollEvent)
				InputHandler.MouseScrollOffset = (0, -1)
			elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
				InputHandler.PutEvent(WindowEvent.MouseClickEvent)
			elif event.type == pygame.MOUSEMOTION:
				InputHandler.MousePos = pygame.mouse.get_pos()
				InputHandler.PutEvent(WindowEvent.MouseMoveEvent)
			elif event.type == pygame.DROPFILE:
				InputHandler.PutEvent(WindowEvent.FileDropEvent)
			elif event.type == pygame.DROPTEXT:
				InputHandler.PutEvent(WindowEvent.TextDropEvent)
	
	def __DefClose(self):
		pygame.display.quit()
	
	def SetTitle(self, title: str):
		pygame.display.set_caption(title)
	
	def Run(self):
		while self.isRunning:
			start = perf_counter()
			self.__DefUpdate()
			self.Update()
			self.updateTime = perf_counter() - start

			start = perf_counter()
			self.Render()
			self.SwapBuffers()
			self.renderTime = perf_counter() - start

			self.frameTime = self.updateTime + self.renderTime
		
		self.Close()
		self.__DefClose()
	
	@property
	def WindowHandle(self):
		return self.__handle