from .glfwWindow import GlfwWindow
from .pygameWindow import PygameWindow
from .windowSpecs import WindowSpecs
from ..enums import WindowAPI
    
class Window:
	@staticmethod
	def Create(specification: WindowSpecs, api: WindowAPI):
		if (api == WindowAPI.Pygame):
			return PygameWindow(specification)
		elif (api == WindowAPI.GLFW):
			return GlfwWindow(specification)
		else:
			raise RuntimeError(f"Invalid windowing API: {api}")