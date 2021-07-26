# from . import enginePreview
from ..enums import Keys
from ..graphics import Renderer
from ..graphics.gl import GLMarshal, GLHelper
from ..input import EventHandler
from ..debugging import Debug, LogLevel
from ..exceptions import GraphicsException, SpykeException
from ..imgui import Imgui
from ..constants import _OPENGL_VER_MAJOR, _OPENGL_VER_MINOR, DEFAULT_ICON_FILEPATH
from .windowSpecs import WindowSpecs

import time
import sys
import atexit
import glfw
import os
import gc
from PIL import Image

class GlfwWindow(object):
	def __init__(self, specification: WindowSpecs, startImgui: bool = False):
		start = time.perf_counter()

		self.isActive = True
		self.baseTitle = specification.title
		self.frameTime = 1.0

		if not glfw.init():
			raise GraphicsException("Cannot initialize GLFW.")

		glfw.set_error_callback(self.__GlfwErrorCb)

		ver = ".".join(str(x) for x in glfw.get_version())
		Debug.Log(f"GLFW version: {ver}", LogLevel.Info)
		
		self.__SetDefaultWindowFlags(specification)
		
		if specification.fullscreen:
			self.__handle = self.__CreateWindowFullscreen(specification)	
			Debug.Log("Window started in fulscreen mode.", LogLevel.Info)
		else:
			self.__handle = self.__CreateWindowNormal(specification)

		glfw.make_context_current(self.__handle)

		self.__GetScreenInfo(specification)

		# enginePreview.RenderPreview()
		# glfw.swap_buffers(self.__handle)

		glfw.set_input_mode(self.__handle, glfw.CURSOR, glfw.CURSOR_NORMAL if specification.cursorVisible else glfw.CURSOR_HIDDEN)

		glfw.set_framebuffer_size_callback(self.__handle, self.__ResizeCb)
		glfw.set_cursor_pos_callback(self.__handle, self.__CursorPosCb)
		glfw.set_window_iconify_callback(self.__handle, self.__IconifyCb)
		glfw.set_mouse_button_callback(self.__handle, self.__MouseCb)
		glfw.set_scroll_callback(self.__handle, self.__MouseScrollCb)
		glfw.set_key_callback(self.__handle, self.__KeyCb)
		glfw.set_window_pos_callback(self.__handle, self.__WindowPosCallback)
		glfw.set_window_focus_callback(self.__handle, self.__WindowFocusCallback)

		#set icon
		if specification.iconFilepath:
			if not os.path.endswith(".ico"):
				raise SpykeException(f"Invalid icon extension: {os.path.splitext(specification.iconFilepath)}.")
			
			self.__LoadIcon(specification.iconFilepath)
		else:
			self.__LoadIcon(DEFAULT_ICON_FILEPATH)

		self.SetVsync(specification.vsync)

		self.positionX, self.positionY = glfw.get_window_pos(self.__handle)

		Renderer.Initialize(Renderer.screenStats.width, Renderer.screenStats.height, specification.samples)

		self.OnLoad()

		if startImgui:
			Imgui.Initialize()
			atexit.register(Imgui.Close)
		
		gc.collect()

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
		Renderer.screenStats.vsync = value

		Debug.Log(f"Vsync set to: {value}.", LogLevel.Info)

	def Run(self):
		isRunning = True

		# enginePreview.CleanupPreview()
		# glfw.swap_buffers(self.__handle)

		while isRunning:
			start = glfw.get_time()

			if glfw.window_should_close(self.__handle):
				EventHandler.WindowClose.Invoke()
				isRunning = False
			
			Imgui._OnFrame()
			
			if self.isActive:
				self.OnFrame()
				glfw.swap_buffers(self.__handle)
			
			glfw.poll_events()

			self.frameTime = glfw.get_time() - start
		
		self.OnClose()
		self.__DefClose()
	
	def __GlfwErrorCb(self, code: int, message: str) -> None:
		raise GraphicsException(f"GLFW error: {message}")

	def __ResizeCb(self, _, width, height):
		Renderer.screenStats.width = width
		Renderer.screenStats.height = height

		EventHandler.WindowResize.Invoke(width, height)

		Debug.Log(f"Window resized to ({width}, {height})", LogLevel.Info)
	
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
			EventHandler.WindowResize.Invoke(Renderer.screenStats.width, Renderer.screenStats.height)
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
			if key == Keys.KeyF2:
				self.SetVsync(not Renderer.screenStats.vsync)
		elif action == glfw.REPEAT:
			EventHandler.KeyDown.Invoke(key, mods, True)
		elif action == glfw.RELEASE:
			EventHandler.KeyUp.Invoke(key)
	
	def __LoadIcon(self, filepath: str) -> None:
		img = Image.open(filepath)
		glfw.set_window_icon(self.__handle, 1, img)
		img.close()

	def __DefClose(self):
		atexit.unregister(GLMarshal.ReleaseAll)
		GLMarshal.ReleaseAll()

		atexit.unregister(Imgui.Close)
		Imgui.Close()

		glfw.destroy_window(self.__handle)
		Debug.Log("Window destroyed.", LogLevel.Info)
		
		glfw.terminate()
		Debug.Log("Glfw terminated.", LogLevel.Info)

		Debug.TryCloseLogFile()

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
		Renderer.screenStats.width, Renderer.screenStats.height = glfw.get_framebuffer_size(self.__handle)
		
		vidmode = glfw.get_video_mode(glfw.get_primary_monitor())
		Renderer.screenStats.refreshRate = vidmode.refresh_rate
		Renderer.screenStats.vsync = spec.vsync
	
	@property
	def WindowHandle(self):
		return self.__handle