#region Import
#from . import enginePreview
from ..graphics.rendering.renderer import Renderer
from .windowSpecs import WindowSpecs
from .window import Window
from ..input.eventHandler import EventHandler, EventType
from ..debugging import Log, LogLevel, Timed, Profiler
from ..imgui import ImGui
from ..managers import ObjectManager

import glfw
import time
import gc
#endregion

Profiler.BeginProfile("profile.json")

class GlfwWindow(Window):
	def __init__(self, specification: WindowSpecs):
		start = time.perf_counter()

		self.width = specification.Width
		self.height = specification.Height
		self.baseTitle = specification.Title

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
		
		if specification.Fullscreen:
			Log("Window started in fulscreen mode.", LogLevel.Info)
			mon = glfw.get_primary_monitor()
			mode = glfw.get_video_mode(mon)
			glfw.window_hint(glfw.RED_BITS, mode.bits.red)
			glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
			glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
			glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

			self.__handle = glfw.create_window(self.width, self.height, self.baseTitle, mon, None)

			self.width, self.height = glfw.get_framebuffer_size(self.__handle)
		else:
			if specification.Resizable:
				glfw.window_hint(glfw.RESIZABLE, glfw.TRUE)
			if specification.Borderless:
				glfw.window_hint(glfw.DECORATED, glfw.FALSE)

			self.__handle = glfw.create_window(self.width, self.height, self.baseTitle, None, None)

		if not self.__handle:
			raise RuntimeError("Cannot create window.")

		glfw.make_context_current(self.__handle)

		#enginePreview.RenderPreview()
		#glfw.swap_buffers(self.__handle)

		if not specification.CursorVisible:
			glfw.set_input_mode(self.__handle, glfw.CURSOR, glfw.CURSOR_HIDDEN)

		glfw.set_framebuffer_size_callback(self.__handle, self.__ResizeCb)
		glfw.set_cursor_pos_callback(self.__handle, self.__CursorPosCb)
		glfw.set_window_iconify_callback(self.__handle, self.__IconifyCb)
		glfw.set_mouse_button_callback(self.__handle, self.__MouseCb)
		glfw.set_scroll_callback(self.__handle, self.__MouseScrollCb)
		glfw.set_key_callback(self.__handle, self.__KeyCb)
		glfw.set_window_pos_callback(self.__handle, self.__WindowPosCallback)

		glfw.swap_interval(1 if specification.Vsync else 0)
		Log(f"Vsync set to: {specification.Vsync}.", LogLevel.Info)

		self.isRunning = True
		self.isActive = True

		self.positionX, self.positionY = glfw.get_window_pos(self.__handle)

		Renderer.Initialize(self.width, self.height)

		self.OnLoad()

		Log(f"GLFW window initialized in {time.perf_counter() - start} seconds.", LogLevel.Info)
	
	def OnFrame(self):
		pass
	
	def OnClose(self):
		pass
	
	def OnLoad(self):
		pass

	def __ResizeCb(self, _, width, height):
		self.width = width
		self.height = height

		EventHandler.PostEvent(EventType.WindowResize, width, height)
	
	def __CursorPosCb(self, _, x, y):
		EventHandler.PostEvent(EventType.MouseMove, x, y)
	
	def __WindowPosCallback(self, _, x, y):
		if (x, y) != (self.positionX, self.positionY):
			EventHandler.PostEvent(EventType.WindowMove, x, y)

			self.positionX = x
			self.positionY = y
	
	def __IconifyCb(self, _, value):
		if value:
			EventHandler.PostEvent(EventType.WindowResize, 0, 0)
			EventHandler.PostEvent(EventType.WindowLostFocus)
			self.isActive = False
		else:
			EventHandler.PostEvent(EventType.WindowResize, self.width, self.height)
			EventHandler.PostEvent(EventType.WindowFocus)
			self.isActive = True
		
	def __MouseCb(self, _, button, action, mods):
		if action == glfw.PRESS:
			EventHandler.PostEvent(EventType.MouseButtonDown, button)
		elif action == glfw.RELEASE:
			EventHandler.PostEvent(EventType.MouseButtonUp, button)
	
	def __MouseScrollCb(self, _, xOffset, yOffset):
		EventHandler.PostEvent(EventType.MouseScroll, xOffset, yOffset)
	
	def __KeyCb(self, _, key, scancode, action, mods):
		if action == glfw.PRESS:
			EventHandler.PostEvent(EventType.KeyDown, key)
		elif action == glfw.RELEASE:
			EventHandler.PostEvent(EventType.KeyUp, key)

	def __DefUpdate(self):
		glfw.poll_events()

		if glfw.window_should_close(self.__handle):
			EventHandler.PostEvent(EventType.WindowClose)
			self.isRunning = False

	def __DefClose(self):
		ImGui.Close()
		ObjectManager.DeleteAll()

		glfw.destroy_window(self.__handle)
		Log("Window destroyed.", LogLevel.Info)
		glfw.terminate()
		Log("Glfw terminated.", LogLevel.Info)
		
		gc.collect()
	
	def SetTitle(self, title: str) -> None:
		glfw.set_window_title(self.__handle, title)
	
	def SwapBuffers(self) -> None:
		glfw.swap_buffers(self.__handle)
	
	def SetVsync(self, value: bool) -> None:
		if value:
			glfw.swap_interval(1)
		else:
			glfw.swap_interval(0)
		
		Log(f"Vsync set to: {value}.", LogLevel.Info)

	def Run(self):
		#enginePreview.CleanupPreview()
		glfw.swap_buffers(self.__handle)

		while self.isRunning:
			start = time.perf_counter()
			
			self.__DefUpdate()

			if self.isActive:
				self.OnFrame()
				glfw.swap_buffers(self.__handle)

			self.frameTime = time.perf_counter() - start
		
		self.OnClose()
		self.__DefClose()

		Profiler.EndProfile()
	
	@property
	def WindowHandle(self):
		return self.__handle