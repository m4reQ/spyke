from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.enums import GLType

from spyke.graphics import gl
from .buffer import Buffer
from OpenGL import GL


class PixelBuffer(Buffer):
    def __init__(self, size: int, data_type: GLType):
        super().__init__(size, data_type)

        self._id = gl.create_buffer()

        GL.glNamedBufferStorage(self.id, self.size,
                                None, GL.GL_DYNAMIC_STORAGE_BIT)

    def bind_load(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self.id)

    def bind_read(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, self.id)

    def unbind(self) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)

    # TODO: Implement pixel buffer objects
