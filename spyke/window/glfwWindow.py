#region Import
#from . import enginePreview
from .windowSpecs import WindowSpecs
from ..graphics.rendering.renderer import Renderer
from ..graphics.contextInfo import ContextInfo
from ..graphics.screenInfo import ScreenInfo
from ..input.eventHandler import EventHandler, EventType
from ..debugging import Debug, LogLevel
from ..exceptions import GraphicsException
from ..imgui import ImGui
from ..memory import GLMarshal

import glfw
import time
import sys
#endregion

class GlfwWindow(object):
	GLMajor = 4
	GLMinor = 5

	def __init__(self, specification: WindowSpecs, startImgui: bool = False):
		start = time.perf_counter()

		self.width = specification.Width
		self.height = specification.Height
		self.baseTitle = specification.Title

		ScreenInfo.Width = specification.Width
		ScreenInfo.Height = specification.Height

		if not glfw.init():
			raise GraphicsException("Cannot initialize GLFW.")
		
		ver = ".".join(str(x) for x in glfw.get_version())
		Debug.Log(f"GLFW version: {ver}", LogLevel.Info)
		
		glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, GlfwWindow.GLMajor)
		glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, GlfwWindow.GLMinor)
		glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
		glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
		glfw.window_hint(glfw.SAMPLES, specification.Samples)
		
		if specification.Fullscreen:
			mon = glfw.get_primary_monitor()
			mode = glfw.get_video_mode(mon)

			glfw.window_hint(glfw.RED_BITS, mode.bits.red)
			glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
			glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
			glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

			self.__handle = glfw.create_window(self.width, self.height, self.baseTitle, mon, None)

			self.width, self.height = glfw.get_framebuffer_size(self.__handle)

			Debug.Log("Window started in fulscreen mode.", LogLevel.Info)
		else:
			glfw.window_hint(glfw.RESIZABLE, specification.Resizable)
			glfw.window_hint(glfw.DECORATED, not specification.Borderless)

			self.__handle = glfw.create_window(self.width, self.height, self.baseTitle, None, None)

		if not self.__handle:
			raise GraphicsException("Cannot create window.")

		glfw.make_context_current(self.__handle)

		ContextInfo.TryGetInfo()

		#enginePreview.RenderPreview()
		#glfw.swap_buffers(self.__handle)

		glfw.set_input_mode(self.__handle, glfw.CURSOR, glfw.CURSOR_NORMAL if specification.CursorVisible else glfw.CURSOR_HIDDEN)

		glfw.set_framebuffer_size_callback(self.__handle, self.__ResizeCb)
		glfw.set_cursor_pos_callback(self.__handle, self.__CursorPosCb)
		glfw.set_window_iconify_callback(self.__handle, self.__IconifyCb)
		glfw.set_mouse_button_callback(self.__handle, self.__MouseCb)
		glfw.set_scroll_callback(self.__handle, self.__MouseScrollCb)
		glfw.set_key_callback(self.__handle, self.__KeyCb)
		glfw.set_window_pos_callback(self.__handle, self.__WindowPosCallback)
		glfw.set_window_focus_callback(self.__handle, self.__WindowFocusCallback)

		glfw.swap_interval(int(specification.Vsync))
		Debug.Log(f"Vsync set to: {specification.Vsync}.", LogLevel.Info)

		self.isRunning = True
		self.isActive = True
		self.frameTime = 0.0
		self.positionX, self.positionY = glfw.get_window_pos(self.__handle)

		Renderer.Initialize(self.width, self.height)

		self.OnLoad()

		if startImgui:
			ImGui.Initialize()

		Debug.Log(f"GLFW window initialized in {time.perf_counter() - start} seconds.", LogLevel.Info)
	
	def OnFrame(self):
		pass
	
	def OnClose(self):
		pass
	
	def OnLoad(self):
		pass

	def __ResizeCb(self, _, width, height):
		self.width = width
		self.height = height

		ScreenInfo.Width = width
		ScreenInfo.Height = height

		EventHandler.PostEvent(EventType.WindowResize, width, height)
	
	def __WindowFocusCallback(self, _, value):
		if value:
			EventHandler.PostEvent(EventType.WindowFocus)
		else:
			EventHandler.PostEvent(EventType.WindowLostFocus)
	
	def __CursorPosCb(self, _, x, y):
		EventHandler.PostEvent(EventType.MouseMove, x, y)
	
	def __WindowPosCallback(self, _, x, y):
		self.positionX = x
		self.positionY = y

		EventHandler.PostEvent(EventType.WindowMove, x, y)

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
			EventHandler.PostEvent(EventType.KeyDown, key, mods, False)
		elif action == glfw.REPEAT:
			EventHandler.PostEvent(EventType.KeyDown, key, mods, True)
		elif action == glfw.RELEASE:
			EventHandler.PostEvent(EventType.KeyUp, key)

	def SetTitle(self, title: str) -> None:
		glfw.set_window_title(self.__handle, title)
	
	def SwapBuffers(self) -> None:
		glfw.swap_buffers(self.__handle)
	
	def SetVsync(self, value: bool) -> None:
		glfw.swap_interval(int(value))
		
		Debug.Log(f"Vsync set to: {value}.", LogLevel.Info)

	def Run(self):
		#enginePreview.CleanupPreview()
		#glfw.swap_buffers(self.__handle)

		while self.isRunning:
			start = time.perf_counter()

			if glfw.window_should_close(self.__handle):
				EventHandler.PostEvent(EventType.WindowClose)
				self.isRunning = False
			
			if self.isActive:
				self.OnFrame()
				glfw.swap_buffers(self.__handle)
			
			glfw.poll_events()

			self.frameTime = time.perf_counter() - start
		
		self.OnClose()

		ImGui.TryClose()
		GLMarshal.ReleaseAll()
		
		glfw.destroy_window(self.__handle)
		Debug.Log("Window destroyed.", LogLevel.Info)
		
		glfw.terminate()
		Debug.Log("Glfw terminated.", LogLevel.Info)

		Debug.CloseLogFile()

		sys.exit()
	
	@property
	def WindowHandle(self):
		return self.__handle