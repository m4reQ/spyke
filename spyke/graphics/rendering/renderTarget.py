from ..buffers import Framebuffer
from ..cameras import Camera

class RenderTarget(object):
    def __init__(self, camera: Camera, framebuffer: Framebuffer = None):
        self.Camera = camera
        self.Framebuffer = framebuffer
        self.ShouldResize = True
    
    @property
    def HasFramebuffer(self):
        return self.Framebuffer != None