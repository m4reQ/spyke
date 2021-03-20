class WindowSpecs(object):
	def __init__(self, width: int, height: int, title: str):
		self.Width = width
		self.Height = height
		self.Samples = 1
		self.Title = title
		self.Vsync = False
		self.Resizable = True
		self.Fullscreen = False
		self.Borderless = False
		self.CursorVisible = True