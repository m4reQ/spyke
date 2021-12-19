from spyke.graphics import gl
from .glBuffer import ABuffer

from OpenGL import GL

class PixelBuffer(ABuffer):
    _BufferUsageFlags = GL.GL_DYNAMIC_STORAGE_BIT

    def __init__(self, size: int):
        super().__init__(size)

        GL.glNamedBufferStorage(self.id, self._size, None, PixelBuffer._BufferUsageFlags)
    
    def BindLoad(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self.id)
    
    def BindRead(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, self.id)
    
    def Unbind(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)
    
    def UploadData(self, size: int, data: memoryview) -> None:
        GL.glNamedBufferSubData(self.id, 0, size, data.obj)
    
    def ReadData(self) -> None:
        raise NotImplementedError