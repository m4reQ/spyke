from pygl import debug as gl_debug
from pygl.buffers import Buffer, BufferFlags
from pygl.sync import Sync
from spyke import debug


class RingBuffer:
    def __init__(self, size: int, flags: BufferFlags, count: int) -> None:
        self._buffers = tuple(Buffer(size, flags) for _ in range(count))
        self._syncs = tuple(Sync() for _ in range(count))
        self._next_buffer = 0
        self._count = count

    @debug.profiled('rendering', 'sync')
    def acquire_next_buffer(self, timeout: int = 0) -> Buffer:
        self._syncs[self._next_buffer].wait(timeout)
        buf = self._buffers[self._next_buffer]

        self._next_buffer = (self._next_buffer + 1) % self._count

        return buf

    @debug.profiled('rendering', 'sync')
    def lock_acquired_buffer(self) -> None:
        self._syncs[(self._next_buffer - 1) % self._count].set()

    def reset_buffer_index(self) -> None:
        self._next_buffer = 0

    def delete(self) -> None:
        for buf in self._buffers:
            buf.delete()

        for sync in self._syncs:
            sync.delete()

    def set_debug_name(self, name: str) -> None:
        for i, buf in enumerate(self._buffers):
            gl_debug.set_object_name(buf, f'{name}_{i}')

        for i, sync in enumerate(self._syncs):
            gl_debug.set_object_name(sync, f'{name}_sync_{i}')

    @property
    def buffers(self) -> tuple[Buffer]:
        return self._buffers

    @property
    def syncs(self) -> tuple[Sync]:
        return self._syncs

    @property
    def buffers_size(self) -> int:
        return self.buffer_size * self._count

    @property
    def buffer_size(self) -> int:
        return self._buffers[0].size
