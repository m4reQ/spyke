class ScreenStats:
    __slots__ = (
        '__weakref__',
        'width',
        'height',
        'vsync',
        'refresh_rate'
    )
    
    def __init__(self):
        self.width: int = 0
        self.height: int = 0
        self.vsync: bool = False
        self.refresh_rate: float = 0.0