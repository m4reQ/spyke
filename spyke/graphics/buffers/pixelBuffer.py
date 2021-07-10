from ..gl import GLHelper
from .aBuffer import ABuffer

from OpenGL import GL

class PixelBuffer(ABuffer):
    _BufferUsageFlags = GL.GL_DYNAMIC_STORAGE_BIT

    def __init__(self, size: int):
        super().__init__(size)

        self._id = GLHelper.CreateBuffer()
        GL.glNamedBufferStorage(self._id, self._size, None, PixelBuffer._BufferUsageFlags)
    
    def BindLoad(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self._id)
    
    def BindRead(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, self._id)
    
    def Unbind(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)
    
    def UploadData(self, size: int, data: memoryview) -> None:
        GL.glNamedBufferSubData(self._id, 0, size, data.obj)
    
    def ReadData(self) -> None:
        raise NotImplementedError
    
    def Delete(self, removeRef: bool) -> None:
        super().Delete(removeRef)