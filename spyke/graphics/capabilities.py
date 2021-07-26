from ..autoslot import Slots

class Capabilities(Slots):
    __slots__ = ("__weakref__", )

    def __init__(self):
        self.nvCommandListEnabled = False
        self.arbBindlessTextureEnabled = False
        self.arbTextureCompressionEnabled = False
        self.intelFramebufferCMAAEnabled = False