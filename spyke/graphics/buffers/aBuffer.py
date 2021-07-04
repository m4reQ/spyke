from ..gl import GLObject, GLHelper

from OpenGL import GL

class ABuffer(GLObject):
    def __init__(self, size: int):
        super().__init__()

        self._size = size
        self._id = GLHelper.CreateBuffer()

    def Delete(self, removeRef: bool) -> None:
        super().Delete(removeRef)
        GL.glDeleteBuffers(1, [self._id])
    
    @property
    def Size(self):
        return self._size