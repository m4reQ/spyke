#region Import
#from . import enginePreview
from ..graphics.rendering.renderer import Renderer
from ..graphics.contextInfo import ContextInfo
from ..graphics.screenInfo import ScreenInfo
from ..graphics.gl import GLMarshal
from ..input.eventHandler import EventHandler
from ..debugging import Debug, LogLevel
from ..exceptions import GraphicsException
from ..imgui import ImGui
from ..constants import _OPENGL_VER_MAJOR, _OPENGL_VER_MINOR
from .windowSpecs import WindowSpecs

import time, sys, atexit, glfw

from spyke.input import eventHandler
#endregion

class GlfwWindow(object):
	def __init__(self, specification: WindowSpecs, startImgui: bool = False):
		start = time.perf_counter()

		self.isActive = True
		self.frameTime = 1.0
		self.baseTitle = specification.title

		if not glfw.init():
			raise GraphicsException("Cannot initialize GLFW.")

		glfw.set_error_callback(self.__GlfwErrorCb)

		ver = ".".join(str(x) for x in glfw.get_version())
		Debug.Log(f"GLFW version: {ver}", LogLevel.Info)
		
		self.__SetDefaultWindowFlags(specification)
		
		if specification.fullscreen:
			self.__handle = self.__CreateWindowFullscreen()	
			Debug.Log("Window started in fulscreen mode.", LogLevel.Info)
		else:
			self.__handle = self.__CreateWindowNormal(specification)

		glfw.make_context_current(self.__handle)

		self.__GetScreenInfo(specification)
		ContextInfo.TryGetInfo()

		#enginePreview.RenderPreview()
		#glfw.swap_buffers(self.__handle)

		glfw.set_input_mode(self.__handle, glfw.CURSOR, glfw.CURSOR_NORMAL if specification.cursorVisible else glfw.CURSOR_HIDDEN)

		glfw.set_framebuffer_size_callback(self.__handle, self.__ResizeCb)
		glfw.set_cursor_pos_callback(self.__handle, self.__CursorPosCb)
		glfw.set_window_iconify_callback(self.__handle, self.__IconifyCb)
		glfw.set_mouse_button_callback(self.__handle, self.__MouseCb)
		glfw.set_scroll_callback(self.__handle, self.__MouseScrollCb)
		glfw.set_key_callback(self.__handle, self.__KeyCb)
		glfw.set_window_pos_callback(self.__handle, self.__WindowPosCallback)
		glfw.set_window_focus_callback(self.__handle, self.__WindowFocusCallback)

		self.SetVsync(specification.vsync)

		self.positionX, self.positionY = glfw.get_window_pos(self.__handle)

		Renderer.Initialize(ScreenInfo.width, ScreenInfo.height, specification.samples)

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

	def SetTitle(self, title: str) -> None:
		glfw.set_window_title(self.__handle, title)
	
	def SwapBuffers(self) -> None:
		glfw.swap_buffers(self.__handle)
	
	def SetVsync(self, value: bool) -> None:
		glfw.swap_interval(int(value))
		ScreenInfo.vsync = value

		Debug.Log(f"Vsync set to: {value}.", LogLevel.Info)

	def Run(self):
		isRunning = True
		#enginePreview.CleanupPreview()
		#glfw.swap_buffers(self.__handle)

		while isRunning:
			start = glfw.get_time()

			if glfw.window_should_close(self.__handle):
				EventHandler.WindowClose.Invoke()
				isRunning = False
			
			if self.isActive:
				self.OnFrame()
				glfw.swap_buffers(self.__handle)
			
			glfw.poll_events()

			self.frameTime = glfw.get_time() - start
		
		self.OnClose()
		self._DefClose()
	
	def __GlfwErrorCb(self, code: int, message: str) -> None:
		raise GraphicsException(f"GLFW error: {message}")

	def __ResizeCb(self, _, width, height):
		ScreenInfo.Width = width
		ScreenInfo.Height = height

		EventHandler.WindowResize.Invoke(width, height)
	
	def __WindowFocusCallback(self, _, value):
		if value:
			EventHandler.WindowFocus.Invoke()
		else:
			EventHandler.WindowLostFocus.Invoke()
	
	def __CursorPosCb(self, _, x, y):
		EventHandler.MouseMove.Invoke(x, y)
	
	def __WindowPosCallback(self, _, x, y):
		self.positionX = x
		self.positionY = y

		EventHandler.WindowMove.Invoke(x, y)

	def __IconifyCb(self, _, value):
		if value:
			EventHandler.WindowResize.Invoke(0, 0)
			EventHandler.WindowLostFocus.Invoke()
			self.isActive = False
		else:
			EventHandler.WindowResize.Invoke(ScreenInfo.width, ScreenInfo.height)
			EventHandler.WindowFocus.Invoke()
			self.isActive = True
		
	def __MouseCb(self, _, button, action, mods):
		if action == glfw.PRESS:
			EventHandler.MouseButtonDown.Invoke(button)
		elif action == glfw.RELEASE:
			EventHandler.MouseButtonUp.Invoke(button)
	
	def __MouseScrollCb(self, _, xOffset, yOffset):
		EventHandler.MouseScroll.Invoke(xOffset, yOffset)
	
	def __KeyCb(self, _, key, scancode, action, mods):
		if action == glfw.PRESS:
			EventHandler.KeyDown.Invoke(key, mods, False)
		elif action == glfw.REPEAT:
			EventHandler.KeyDown.Invoke(key, mods, True)
		elif action == glfw.RELEASE:
			EventHandler.KeyUp.Invoke(key)

	def _DefClose(self):
		atexit.unregister(GLMarshal.ReleaseAll)
		GLMarshal.ReleaseAll()

		ImGui.TryClose()

		glfw.destroy_window(self.__handle)
		Debug.Log("Window destroyed.", LogLevel.Info)
		
		glfw.terminate()
		Debug.Log("Glfw terminated.", LogLevel.Info)

		Debug.CloseLogFile()

		sys.exit()
	
	def __CreateWindowNormal(self, spec):
		glfw.window_hint(glfw.RESIZABLE, spec.resizable)
		glfw.window_hint(glfw.DECORATED, not spec.borderless)

		return glfw.create_window(spec.width, spec.height, self.baseTitle, None, None)

	def __CreateWindowFullscreen(self, spec):
		mon = glfw.get_primary_monitor()
		mode = glfw.get_video_mode(mon)

		glfw.window_hint(glfw.RED_BITS, mode.bits.red)
		glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
		glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
		glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

		return glfw.create_window(spec.width, spec.height, self.baseTitle, mon, None)

	def __SetDefaultWindowFlags(self, spec):
		glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, _OPENGL_VER_MAJOR)
		glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, _OPENGL_VER_MINOR)
		glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
		glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
		glfw.window_hint(glfw.SAMPLES, spec.samples)

	def __GetScreenInfo(self, spec):
		ScreenInfo.width, ScreenInfo.height = glfw.get_framebuffer_size(self.__handle)
		
		vidmode = glfw.get_video_mode(glfw.get_primary_monitor())
		ScreenInfo.refreshRate = vidmode.refresh_rate

		ScreenInfo.vsync = spec.vsync
	
	@property
	def WindowHandle(self):
		return self.__handle