from ...debugging import Debug, LogLevel
from ..gl import AGLObject, GLHelper

from OpenGL import GL

class ABuffer(AGLObject):
    def __init__(self, size: int, dataType: GL.GLenum):
        super().__init__()

        self.dataType = dataType

        self._size = size
        self._id = GLHelper.CreateBuffer()

    def Delete(self, removeRef: bool) -> None:
        super().Delete(removeRef)
        GL.glDeleteBuffers(1, [self._id])
    
    @property
    def Size(self):
        return self._size

class AMappable(ABuffer):
    _BufferUsageFlags = GL.GL_MAP_WRITE_BIT | GL.GL_MAP_PERSISTENT_BIT | GL.GL_MAP_COHERENT_BIT

    def __init__(self, size: int, dataType: GL.GLenum):
        super().__init__(size, dataType)
        self._alreadyMapped = False

    def _MapPersistent(self):
        if self._alreadyMapped:
            Debug.Log("Buffer is already persistently mapped.", LogLevel.Warning)
            return

        self._pointer = GL.glMapNamedBufferRange(self._id, 0, self._size, AMappable._BufferUsageFlags)
        Debug.Log(f"Buffer (id: {self._id}) has been persistently mapped to {hex(self._pointer)}.", LogLevel.Info)
        self._alreadyMapped = True
    
    @property
    def Pointer(self):
        return self._pointer