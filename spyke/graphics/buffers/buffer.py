from __future__ import annotations
import threading

import typing as t
import logging
import abc

from OpenGL import GL
import numpy as np
import glm

from spyke.enums import GLType
from spyke.exceptions import GraphicsException
from spyke.graphics import gl
from spyke.utils import convert
from spyke import debug

_logger = logging.getLogger(__name__)

_DT = t.Union[int, float, np.ndarray, glm.mat2, glm.mat3, glm.mat4, glm.vec2, glm.vec3, glm.vec4]

class BufferBase(gl.GLObject, abc.ABC):
    @staticmethod
    def bind_pbo_load(pbo: BufferBase) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, pbo.id)

    @staticmethod
    def bind_pbo_read(pbo: BufferBase) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, pbo.id)

    @staticmethod
    def unbind_pbo() -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)

    @staticmethod
    def bind_ubo(ubo: BufferBase) -> None:
        GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, ubo.id)

    @staticmethod
    def bind_to_uniform(ubo: BufferBase, index: int) -> None:
        GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, index, ubo.id)

    @debug.profiled('graphics')
    def __init__(self, size: int, data_type: GLType):
        super().__init__()

        self._id = gl.create_buffer()
        self._size = size
        self.data_type: GLType = data_type

        _logger.debug('%s created succesfully (data size: %.3fkB).', self, self.size / 1000.0)

    @debug.profiled('graphics')
    def _delete(self) -> None:
        GL.glDeleteBuffers(1, [self.id])

    @property
    def size(self) -> int:
        return self._size

class StaticBuffer(BufferBase):
    def __init__(self, data: t.Union[np.ndarray, list], data_type: GLType):
        size = len(data) * convert.gl_type_to_size(data_type)
        super().__init__(size, data_type)

        if isinstance(data, list):
            np_data = np.asarray(
                data, dtype=convert.gl_type_to_np_type(data_type))
        elif isinstance(data, np.ndarray):
            np_data = data
        else:
            raise GraphicsException(f'Invalid data format: {type(data)}.')

        GL.glNamedBufferStorage(self.id, self.size, np_data, 0)

class DynamicBuffer(BufferBase):
    def __init__(self, size: int, data_type: GLType):
        super().__init__(size, data_type)

        self._data = np.empty((size // convert.gl_type_to_size(data_type),),
                              dtype=convert.gl_type_to_np_type(data_type))
        self._offset = 0
        self._lock = threading.Lock()

        GL.glNamedBufferStorage(self.id, self.size, None, GL.GL_DYNAMIC_STORAGE_BIT)

    @debug.profiled('graphics')
    def flip(self) -> None:
        '''
        Transfers data from local storage to GPU buffer memory.
        '''
        
        GL.glNamedBufferSubData(self.id, 0, self._offset * convert.gl_type_to_size(self.data_type), self._data)
        self.reset()

    def reset(self) -> None:
        self._offset = 0

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

    @debug.profiled('graphics')
    def store(self, data: _DT) -> None:
        '''
        Stores data in CPU-side memory to be later transferred to GPU buffer
        memory using `DynamicBuffer.flip`. This function is thread-safe.
        
        @data: Data to be stored.
        '''
        
        _data, elements_count, size = self._convert_data(data)

        self._check_overflow(size)

        with self._lock:
            self._data[self._offset:self._offset + elements_count] = _data
            self._offset += elements_count

    @t.overload
    def store_direct(self, data: int) -> None: ...

    @t.overload
    def store_direct(self, data: float) -> None: ...

    @t.overload
    def store_direct(self, data: np.ndarray) -> None: ...

    @t.overload
    def store_direct(self, data: glm.mat2) -> None: ...

    @t.overload
    def store_direct(self, data: glm.mat3) -> None: ...

    @t.overload
    def store_direct(self, data: glm.mat4) -> None: ...
    
    @t.overload
    def store_direct(self, data: glm.vec2) -> None: ...
    
    @t.overload
    def store_direct(self, data: glm.vec3) -> None: ...
    
    @t.overload
    def store_direct(self, data: glm.vec4) -> None: ...

    @debug.profiled('graphics')
    @debug.require_context
    def store_direct(self, data: _DT) -> None:
        '''
        Stores data directly in GPU buffer memory, instead of temporarily
        copying it to CPU-side memory. This function requires OpenGL context
        to be set while it is called and is not thread-safe.
        
        @data: Data to be stored.
        '''
        
        _data, _, size = self._convert_data(data)
        
        self._check_overflow(size)
        
        GL.glNamedBufferSubData(self.id, 0, size, _data)

    @debug.profiled('graphics')
    def _convert_data(self, data: _DT) -> tuple[t.Iterable, int, int]:
        size: int
        elements_count: int
        _data: t.Iterable

        if isinstance(data, (int, float)) or isinstance(data, float):
            size = 4
            elements_count = 1
            _data = [data]
        elif isinstance(data, np.ndarray):
            size = data.nbytes
            elements_count = data.size
            _data = data
        elif isinstance(data, (glm.mat2, glm.mat3, glm.mat4)):
            size = data.length() ** 2 * 4
            elements_count = data.length() ** 2
            _data = np.asarray(glm.transpose(data), dtype=np.float32).flatten()
        elif isinstance(data, (glm.vec2, glm.vec3, glm.vec4)):
            size = len(data) * 4
            elements_count = len(data)
            _data = data
        
        return (_data, elements_count, size)
    
    def _check_overflow(self, nbytes: int) -> None:
        if self._offset * convert.gl_type_to_size(self.data_type) + nbytes > self.size:
            # TODO: Add BufferOverflowException class
            raise GraphicsException(f'Transfer of {nbytes} bytes at {self} would cause buffer overflow.')
