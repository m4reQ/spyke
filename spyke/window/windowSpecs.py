class WindowSpecs(object):
	def __init__(self, width: int, height: int, title: str, glMajor: int, glMinor: int):
		self.Width = width
		self.Height = height
		self.GlVersionMajor = glMajor
		self.GlVersionMinor = glMinor
		self.Samples = 1
		self.Title = title
		self.Vsync = False
		self.Resizable = True
		self.Fullscreen = False
		self.Borderless = False
		self.CursorVisible = True