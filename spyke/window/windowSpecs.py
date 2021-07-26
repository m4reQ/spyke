from ..autoslot import Slots

class WindowSpecs(Slots):
	__slots__ = ("__weakref__", )
	
	def __init__(self, width: int, height: int, title: str):
		self.width = width
		self.height = height
		self.samples = 1
		self.title = title
		self.vsync = True
		self.resizable = True
		self.fullscreen = False
		self.borderless = False
		self.cursorVisible = True
		self.iconFilepath = ""