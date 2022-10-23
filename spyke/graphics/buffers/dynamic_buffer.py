import threading
import typing as t

import glm
import glm_typing
import numpy as np
import numpy.typing as npt
from OpenGL import GL
from spyke import debug, exceptions
from spyke.enums import BufferStorageFlags

from .buffer import BufferBase

_DataType = glm_typing.AnyAnyVecAny | glm_typing.AnyAnyMatrixSquare | glm_typing.Number | np.ndarray # type: ignore

class DynamicBuffer(BufferBase):
    def __init__(self,
                 count: int,
                 dtype: npt.DTypeLike=np.float32,
                 generate_storage: bool = True):
        self._stride = np.dtype(dtype).itemsize

        super().__init__(
            count * self._stride,
            BufferStorageFlags.DynamicStorageBit)

        self._lock = threading.Lock()
        self._current_offset = 0
        self._data: np.ndarray | None = None
        if generate_storage:
            self._data = np.empty(
                (count,),
                dtype=dtype)

    @debug.profiled('graphics', 'buffers', 'runtime')
    def flip(self) -> None:
        '''
        Transfers data from local storage to GPU buffer memory.
        '''

        self.ensure_initialized()

        GL.glNamedBufferSubData(self.id, 0, self._current_offset * self._stride, self._data)
        self._current_offset = 0

    @t.overload
    def store(self, data: int) -> None: ...

    @t.overload
    def store(self, data: float) -> None: ...

    @t.overload
    def store(self, data: np.ndarray) -> None: ...

    @t.overload
    def store(self, data: glm.mat2) -> None: ...

    @t.overload
    def store(self, data: glm.mat3) -> None: ...

    @t.overload
    def store(self, data: glm.mat4) -> None: ...

    @t.overload
    def store(self, data: glm.vec2) -> None: ...

    @t.overload
    def store(self, data: glm.vec3) -> None: ...

    @t.overload
    def store(self, data: glm.vec4) -> None: ...

    @debug.profiled('graphics', 'buffers', 'rendering')
    def store(self, data: _DataType) -> None:
        '''
        Stores data in CPU-side memory to be later transferred to GPU buffer
        memory using `DynamicBuffer.flip`. This function is thread-safe.

        @data: Data to be stored.
        '''

        assert self._data is not None, f'Buffer with id {self.id} has no CPU-side storage'

        _data, elements_count = _convert_data(data)
        with self._lock:
            self._check_overflow(elements_count)

            self._data[self._current_offset:self._current_offset + elements_count] = _data
            self._current_offset += elements_count

    @t.overload
    def store_direct(self, data: int, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: float, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: np.ndarray, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: glm.mat2, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: glm.mat3, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: glm.mat4, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: glm.vec2, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: glm.vec3, offset: int = 0) -> None: ...

    @t.overload
    def store_direct(self, data: glm.vec4, offset: int = 0) -> None: ...

    @debug.profiled('graphics', 'buffers', 'rendering')
    def store_direct(self, data: _DataType, offset: int = 0) -> None:
        '''
        Stores data directly in GPU buffer memory, instead of temporarily
        copying it to CPU-side memory. This function requires OpenGL context
        to be set while it is called and is not thread-safe.

        @data: Data to be stored.
        '''

        self.ensure_initialized()

        _data, elements_count = _convert_data(data)
        self._check_overflow(elements_count)

        GL.glNamedBufferSubData(self.id, offset, elements_count * self._stride, _data)

    def _check_overflow(self, elements_count: int) -> None:
        data_size = elements_count * self._stride

        if self._current_offset * self._stride + data_size > self.size:
            raise exceptions.BufferOverflowException(self.id, data_size)

@debug.profiled('graphics', 'buffers', 'convert')
def _convert_data(data: _DataType) -> tuple[t.Iterable, int]:
    elements_count: int
    _data: t.Iterable

    if isinstance(data, int | float):
        elements_count = 1
        _data = [data]
    elif isinstance(data, np.ndarray):
        elements_count = data.size
        _data = data
    elif isinstance(data, glm.mat2 | glm.mat3 | glm.mat4):
        elements_count = data.length() ** 2
        _data = np.asarray(glm.transpose(data), dtype=np.float32).flatten()
    elif isinstance(data, glm.vec2 | glm.vec3 | glm.vec4):
        elements_count = len(data)
        _data = data

    return (_data, elements_count)
