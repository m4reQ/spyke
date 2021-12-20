class WindowSpecs:
	__slots__ = (
		'__weakref__',
		'width',
		'height',
		'samples',
		'title',
		'vsync',
		'resizable',
		'fullscreen',
		'borderless',
		'cursor_visible',
		'icon_filepath'
	)
	
	def __init__(self, width: int, height: int, title: str):
		self.width: int = width
		self.height: int = height
		self.samples: int = 1
		self.title: str = title
		self.vsync: bool = True
		self.resizable: bool = True
		self.fullscreen: bool = False
		self.borderless: bool = False
		self.cursor_visible: bool = True
		self.icon_filepath: str = ""