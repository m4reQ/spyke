class ScreenStats(object):
    __slots__ = ("width", "height", "vsync", "refreshRate")

    def __init__(self):
        self.width = 0
        self.height = 0
        self.vsync = False
        self.refreshRate = 0.0