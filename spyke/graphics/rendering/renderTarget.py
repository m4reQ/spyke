from ..buffers import Framebuffer
from ..cameras import Camera

class RenderTarget(object):
    def __init__(self, camera: Camera, framebuffer: Framebuffer = None):
        self.Camera = camera
        self.Framebuffer = framebuffer
        self.ContainsPass = False
    
    @property
    def Width(self):
        return self.Framebuffer.Width
    
    @property
    def Height(self):
        return self.Framebuffer.Height
    
    @property
    def Samples(self):
        return self.Framebuffer.Samples
    
    @property
    def HasFramebuffer(self):
        return self.Framebuffer != None