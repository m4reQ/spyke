import abc
import ctypes as ct

from OpenGL import GL

from spyke import debug
from spyke.enums import BufferStorageFlags
from spyke.graphics.opengl_object import OpenglObjectBase


class BufferBase(OpenglObjectBase, abc.ABC):
    @debug.profiled('graphics', 'buffers', 'rendering')
    @staticmethod
    def unbind_pbo() -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)

    def __init__(self, size: int, storage_flags: BufferStorageFlags = BufferStorageFlags._None):
        super().__init__()

        self._size = size
        self._storage_flags = storage_flags

    @debug.profiled('graphics', 'buffers', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        GL.glCreateBuffers(1, ct.pointer(self._id))
        GL.glNamedBufferStorage(self.id, self._size, None, self._storage_flags)

    @debug.profiled('graphics', 'cleanup')
    def delete(self) -> None:
        super().delete()

        GL.glDeleteBuffers(1, ct.pointer(self._id))

    @debug.profiled('graphics', 'buffers', 'rendering')
    def bind_pbo_load(self) -> None:
        '''
        Binds buffer as pixel unpack buffer.
        '''

        self.ensure_initialized()
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, self.id)

    @debug.profiled('graphics', 'buffers', 'rendering')
    def bind_pbo_read(self) -> None:
        '''
        Binds buffer as pixel pack buffer.
        '''

        self.ensure_initialized()
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, self.id)

    @debug.profiled('graphics', 'buffers', 'rendering')
    def bind_ubo(self) -> None:
        '''
        Binds buffer as uniform buffer.
        '''

        self.ensure_initialized()
        GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, self.id)

    @debug.profiled('graphics', 'buffers')
    def bind_to_uniform(self, index: int) -> None:
        self.ensure_initialized()
        GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, index, self.id)

    @property
    def size(self) -> int:
        return self._size
