from .aBuffer import ABuffer
from ...constants import _NP_FLOAT

from OpenGL import GL

class AVertexBuffer(ABuffer):
    def __init__(self, size: int, data: list, storageFlags: GL.GLenum):
        super().__init__(size, data, _NP_FLOAT, storageFlags)