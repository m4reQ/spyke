class RenderStats:
	__slots__ = (
		'__weakref__',
		'draws_count',
		'vertex_count',
		'draw_time',
		'video_memory_used'
	)

	def __init__(self):
		self.draws_count: int = 0
		self.vertex_count: int = 0
		self.draw_time: float = 1.0
		self.video_memory_used: float = 0.0
	
	def Clear(self):
		self.draws_count = 0
		self.vertex_count = 0
		self.draw_time = 1.0
		self.video_memory_used = 0.0