class WindowSpecs(object):
	def __init__(self, width: int, height: int, title: str, glMajor: int, glMinor: int):
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