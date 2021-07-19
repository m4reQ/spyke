class WindowSpecs(object):
	__slots__ = ("width", "height", "samples", "title", "vsync", "resizable", "fullscreen", "borderless", "cursorVisible", "iconFilepath")

	def __init__(self, width: int, height: int, title: str):
		self.width = width
		self.height = height
		self.samples = 1
		self.title = title
		self.vsync = False
		self.resizable = True
		self.fullscreen = False
		self.borderless = False
		self.cursorVisible = True
		self.iconFilepath = ""