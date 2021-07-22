from ..autoslot import WeakSlots

class WindowSpecs(WeakSlots):
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