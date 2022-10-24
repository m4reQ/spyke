import ctypes as ct
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
                 dtype: npt.DTypeLike=np.float32):
        self._stride = np.dtype(dtype).itemsize

        super().__init__(
            count * self._stride,
            BufferStorageFlags.MapPersistentBit | BufferStorageFlags.MapCoherentBit | BufferStorageFlags.MapWriteBit) # type: ignore

        self._lock = threading.Lock()
        self._current_offset = 0
        self._dtype = dtype
        self._elements_count = count
        self._data: np.ndarray

    @debug.profiled('graphics', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        ptr = GL.glMapNamedBufferRange(self.id, 0, self.size, GL.GL_MAP_WRITE_BIT | GL.GL_MAP_PERSISTENT_BIT | GL.GL_MAP_COHERENT_BIT)
        self._data = _ptr_to_np_array(ptr, self._dtype, self._elements_count)

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
        Stores data in buffer's memory.

        @data: Data to be stored.
        '''

        self.ensure_initialized()

        _data, elements_count = _convert_data(data)
        with self._lock:
            self._check_overflow(elements_count)

            self._data[self._current_offset:self._current_offset + elements_count] = _data
            self._current_offset += elements_count

    def reset(self) -> None:
        self._current_offset = 0

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

def _ptr_to_np_array(ptr: int, dtype: npt.DTypeLike, elements_count: int) -> np.ndarray:
    ptr_type = ct.POINTER(np.ctypeslib.as_ctypes_type(dtype)) # type: ignore

    return np.ctypeslib.as_array(ct.cast(ptr, ptr_type), (elements_count, ))
