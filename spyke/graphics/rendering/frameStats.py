class FrameStats:
    __slots__ = (
        '__weakref__',
        'frametime',
        'drawtime',
        'draw_calls',
        'accumulated_vertex_count',
        'window_active',
        'video_memory_used'
    )

    def __init__(self):
        self.frametime: float = 1.0
        self.drawtime: float = 0.0
        self.draw_calls: int = 0
        self.accumulated_vertex_count: int = 0
        self.window_active: bool = True
        self.video_memory_used: int = -1
