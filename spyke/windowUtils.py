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

class WindowAPI:
	GLFW = "API::GLFW"
	Pygame = "API::Pygame"
	NoAPI = "API::None"