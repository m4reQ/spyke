from .windowSpecs import WindowSpecs
from ..inputHandler import InputHandler
from ..debug import Log, LogLevel, Timer
from ..enums import WindowAPI, WindowEvent

import glfw

class GlfwWindow(object):
	Api = WindowAPI.GLFW

	def __init__(self, specification: WindowSpecs):
		Timer.Start()

		self.width = specification.Width
		self.height = specification.Height
		self.baseTitle = specification.Title

		self.specs = specification

		if not glfw.init():
			raise RuntimeError("Cannot initialize GLFW.")
		
		ver = ".".join(str(x) for x in glfw.get_version())
		Log(f"GLFW version: {ver}", LogLevel.Info)

		glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, specification.GlVersionMajor)
		glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, specification.GlVersionMinor)
		glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
		glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
		if specification.Multisample:
			glfw.window_hint(glfw.SAMPLES, specification.Samples)
		
		if self.specs.Fullscreen:
			mon = glfw.get_primary_monitor()
			mode = glfw.get_video_mode(mon)
			glfw.window_hint(glfw.RED_BITS, mode.bits.red)
			glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
			glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
			glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

			self.__handle = glfw.create_window(self.width, self.height, self.baseTitle, mon, None)

			self.width, self.height = glfw.get_framebuffer_size(self.__handle)
		else:
			if self.specs.Resizable:
				glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
			if self.specs.Borderless:
				glfw.window_hint(glfw.DECORATED, glfw.FALSE)

			self.__handle = glfw.create_window(self.width, self.height, self.baseTitle, None, None)

		if not self.__handle:
			raise RuntimeError("Cannot create window.")

		glfw.make_context_current(self.__handle)

		if not self.specs.CursorVisible:
			glfw.set_input_mode(self.__handle, glfw.CURSOR, glfw.CURSOR_HIDDEN)

		glfw.set_framebuffer_size_callback(self.__handle, self.__ResizeCb)
		glfw.set_cursor_pos_callback(self.__handle, self.__CursorPosCb)
		glfw.set_window_iconify_callback(self.__handle, self.__IconifyCb)
		glfw.set_mouse_button_callback(self.__handle, self.__MouseCb)
		glfw.set_scroll_callback(self.__handle, self.__MouseScrollCb)
		glfw.set_key_callback(self.__handle, self.__KeyCb)
		glfw.set_window_pos_callback(self.__handle, self.__WindowPosCallback)

		if specification.Vsync:
			glfw.swap_interval(1)
		else:
			glfw.swap_interval(0)

		self.isRunning = True
		self.isActive = True

		self.updateTime = 1.0
		self.renderTime = 1.0
		self.frameTime = 1.0

		self.position = (0, 0)

		InputHandler.PutEvent(WindowEvent.ResizeEvent)

		Log(f"GLFW window initialized in {Timer.Stop()} seconds.", LogLevel.Info)
	
	def SwapBuffers(self):
		glfw.swap_buffers(self.__handle)

	def OnFrame(self):
		pass
	
	def Close(self):
		pass

	def __ResizeCb(self, _, width, height):
		self.width = width
		self.height = height

		InputHandler.PutEvent(WindowEvent.ResizeEvent)
	
	def __CursorPosCb(self, _, x, y):
		if InputHandler.MousePos != (x, y):
			InputHandler.PutEvent(WindowEvent.MouseMoveEvent)
		
		InputHandler.MousePos = (x, y)
	
	def __WindowPosCallback(self, _, x, y):
		self.position = (x, y)
	
	def __IconifyCb(self, _, value):
		if value == 1:
			InputHandler.PutEvent(WindowEvent.IconifiedEvent)
			self.isActive = False
		elif value == 0:
			self.isActive = True
		
	def __MouseCb(self, _, button, action, mods):
		InputHandler.PutEvent(WindowEvent.MouseClickEvent)

		if action == glfw.PRESS:
			InputHandler.AddButton(button)
	
	def __MouseScrollCb(self, _, xOffset, yOffset):
		InputHandler.PutEvent(WindowEvent.MouseScrollEvent)

		InputHandler.MouseScrollOffset = (xOffset, yOffset)
	
	def __KeyCb(self, _, key, scancode, action, mods):
		InputHandler.PutEvent(WindowEvent.KeyEvent)

		InputHandler.AddKey(key)

	def __DefUpdate(self):
		InputHandler.ClearEvents()
		glfw.poll_events()

		if glfw.window_should_close(self.__handle):
			InputHandler.PutEvent(WindowEvent.CloseEvent)
			self.isRunning = False

	def __DefClose(self):
		glfw.terminate()
	
	def SetTitle(self, title: str):
		glfw.set_window_title(self.__handle, title)

	def Run(self):
		while self.isRunning:
			Timer.Start()
			
			self.__DefUpdate()
			if self.isActive:
				self.OnFrame()
				self.SwapBuffers()

			self.frameTime = Timer.Stop()
		
		self.Close()
		self.__DefClose()
	
	@property
	def WindowHandle(self):
		return self.__handle