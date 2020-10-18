from ..buffers import Framebuffer
from ..cameras import OrthographicCamera

class RenderTarget(object):
    def __init__(self, camera: OrthographicCamera, framebuffer: Framebuffer = None):
        self.Camera = camera
        self.Framebuffer = framebuffer
    
    @property
    def HasFramebuffer(self):
        return self.Framebuffer != None