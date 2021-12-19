from spyke import debug
from spyke.enums import GLType
from spyke.exceptions import GraphicsException
from spyke.graphics import gl
from spyke.utils import convert
from OpenGL import GL
from typing import Union
import numpy as np

class ABuffer(gl.GLObject):
    def __init__(self, size: int, data_type: GLType):
        super().__init__()

        self._id = gl.create_buffer()
        self._size = size
        self.data_type = data_type

        debug.log_info(f'{self} created succesfully (data size: {self.size / 1000.0}kB).')
    
    def delete(self) -> None:
        GL.glDeleteBuffers(1, [self.id])
    
    @property
    def size(self) -> int:
        return self._size

class StaticBuffer(ABuffer):
    def __init__(self, data: Union[np.ndarray, list], data_type: GLType):
        size = len(data) * convert.gl_type_to_size(data_type)
        super().__init__(size, data_type)

        if isinstance(data, list):
            np_data = np.asarray(data, dtype=convert.gl_type_to_np_type(data_type))
        elif isinstance(data, np.ndarray):
            np_data = data
        else:
            raise GraphicsException(f'Invalid data format: {type(data)}.')

        GL.glNamedBufferStorage(self.id, self.size, np_data, 0)

class DynamicBuffer(ABuffer):
    def __init__(self, size: int, data_type: GLType):
        super().__init__(size, data_type)

        self._data = np.empty((size // convert.gl_type_to_size(data_type),), dtype=convert.gl_type_to_np_type(data_type))
        self._offset = 0

        GL.glNamedBufferStorage(self.id, self.size, None, GL.GL_DYNAMIC_STORAGE_BIT)
    
    def flip(self) -> None:
        GL.glNamedBufferSubData(self.id, 0, self._offset, self.data)
        self._offset = 0
    
    def add_data(self, data: np.ndarray, offset: int=-1) -> None:
        _offset = offset if offset != -1 else self._offset
        if _offset + data.nbytes > self.size:
            raise GraphicsException(f'Transfer of {data.nbytes} bytes at {self} would cause buffer overflow.')
        
        new_size = _offset + data.nbytes
        if new_size > self._offset:
            self._offset = new_size

        start = _offset // convert.gl_type_to_size(self.data_type)
        end = start + data.size
        self._data[start:end] = data
    
    @property
    def data(self) -> np.ndarray:
        return self._data