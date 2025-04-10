from spyke import debug
from spyke.graphics import gl


class RingBuffer:
    def __init__(self, size: int, flags: gl.BufferFlag, count: int) -> None:
        self._buffers = tuple(gl.Buffer(size, flags) for _ in range(count))
        self._syncs = tuple(gl.Sync() for _ in range(count))
        self._next_buffer = 0
        self._count = count

    @debug.profiled
    def acquire_next_buffer(self, timeout: int = 0) -> gl.Buffer:
        self._syncs[self._next_buffer].wait(timeout)
        buf = self._buffers[self._next_buffer]

        self._next_buffer = (self._next_buffer + 1) % self._count

        return buf

    @debug.profiled
    def lock_acquired_buffer(self) -> None:
        self._syncs[(self._next_buffer - 1) % self._count].set()

    def is_next_buffer_available(self) -> bool:
        return self._syncs[self._next_buffer].is_signaled()

    def reset_buffer_index(self) -> None:
        self._next_buffer = 0

    def delete(self) -> None:
        for buf in self._buffers:
            buf.delete()

        for sync in self._syncs:
            sync.delete()

    def set_debug_name(self, name: str) -> None:
        for i, buf in enumerate(self._buffers):
            gl.set_object_name(buf, f'{name}_{i}')

        for i, sync in enumerate(self._syncs):
            gl.set_object_name(sync, f'{name}_sync_{i}')

    @property
    def buffers(self) -> tuple[gl.Buffer, ...]:
        return self._buffers

    @property
    def syncs(self) -> tuple[gl.Sync, ...]:
        return self._syncs

    @property
    def buffers_size(self) -> int:
        return self.buffer_size * self._count

    @property
    def buffer_size(self) -> int:
        return self._buffers[0].size
