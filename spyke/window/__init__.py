from .glfwWindow import GlfwWindow
from .pygameWindow import PygameWindow
from ..enums import WindowAPI

class WindowSpecs(object):
	def __init__(self, width, height, title, glMajor, glMinor):
		self.Width = width
		self.Height = height
		self.Title = title
		self.GlVersionMajor = glMajor
		self.GlVersionMinor = glMinor
		self.Vsync = False
		self.Multisample = False
		self.Samples = 4
		self.Resizable = True
		self.Fullscreen = False
		self.Borderless = False
		self.CursorVisible = True
    
class Window:
	@staticmethod
	def Create(specification: WindowSpecs, api: WindowAPI):
		if (api == WindowAPI.Pygame):
			return PygameWindow(specification)
		elif (api == WindowAPI.GLFW):
			return GlfwWindow(specification)
		else:
			raise RuntimeError(f"Invalid windowing API: {api}")