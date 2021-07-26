from ..autoslot import Slots

class ScreenStats(Slots):
    __slots__ = ("__weakref__", )
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.vsync = False
        self.refreshRate = 0.0