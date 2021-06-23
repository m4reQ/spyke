from ..gl import GLObject, GLHelper
from ...constants import _NP_FLOAT

from OpenGL import GL
import numpy as np

class ABuffer(GLObject):
    def __init__(self, size: int, data: list, npDtype: str, storageFlags: GL.GLenum):
        super().__init__()

        self._size = size
        self._id = GLHelper.CreateBuffer()

        data = data if not data else np.asarray(data, dtype=npDtype)
        GL.glNamedBufferStorage(self._id, size, data, storageFlags)

    def Delete(self, removeRef: bool) -> None:
        super().Delete(removeRef)
        GL.glDeleteBuffers(1, [self._id])
    
    @property
    def Size(self):
        return self._size