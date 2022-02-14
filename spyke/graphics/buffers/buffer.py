from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.enums import GLType
    from typing import Union

import logging
from spyke.exceptions import GraphicsException
from spyke.graphics import gl
from spyke.utils import convert
from OpenGL import GL
import numpy as np
from abc import ABC


class Buffer(gl.GLObject, ABC):
    @staticmethod
    def bind_pbo_load(pbo: Buffer) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, pbo.id)

    @staticmethod
    def bind_pbo_read(pbo: Buffer) -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, pbo.id)

    @staticmethod
    def unbind_pbo() -> None:
        GL.glBindBuffer(GL.GL_PIXEL_PACK_BUFFER, 0)
        GL.glBindBuffer(GL.GL_PIXEL_UNPACK_BUFFER, 0)

    @staticmethod
    def bind_ubo(ubo: Buffer) -> None:
        GL.glBindBuffer(GL.GL_UNIFORM_BUFFER, ubo.id)

    @staticmethod
    def bind_to_uniform(ubo: Buffer, index: int) -> None:
        GL.glBindBufferBase(GL.GL_UNIFORM_BUFFER, index, ubo.id)

    def __init__(self, size: int, data_type: GLType):
        super().__init__()

        self._id = gl.create_buffer()
        self._size = size
        self.data_type: GLType = data_type

        logging.log(logging.SP_INFO,
                    f'{self} created succesfully (data size: {self.size / 1000.0}kB).')

    def _delete(self) -> None:
        GL.glDeleteBuffers(1, [self.id])

    @property
    def size(self) -> int:
        return self._size


class StaticBuffer(Buffer):
    def __init__(self, data: Union[np.ndarray, list], data_type: GLType):
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


class DynamicBuffer(Buffer):
    def __init__(self, size: int, data_type: GLType):
        super().__init__(size, data_type)

        self._data = np.empty((size // convert.gl_type_to_size(data_type),),
                              dtype=convert.gl_type_to_np_type(data_type))
        self._offset = 0

        GL.glNamedBufferStorage(self.id, self.size, None,
                                GL.GL_DYNAMIC_STORAGE_BIT)

    def flip(self) -> None:
        GL.glNamedBufferSubData(
            self.id, 0, self._offset * convert.gl_type_to_size(self.data_type), self._data)
        self._offset = 0

    def reset(self) -> None:
        self._offset = 0

    def add_data(self, data: np.ndarray) -> None:
        if self._would_overflow(data.nbytes):
            raise GraphicsException(
                f'Transfer of {data.nbytes} bytes at {self} would cause buffer overflow.')

        self._data[self._offset:self._offset + data.size] = data
        self._offset += data.size

    def add_data_direct(self, data: np.ndarray) -> None:
        if self._would_overflow(data.nbytes):
            raise GraphicsException(
                f'Transfer of {data.nbytes} bytes at {self} would cause buffer overflow.')

        GL.glNamedBufferSubData(self.id, 0, data.nbytes, data)

    def _would_overflow(self, nbytes: int) -> bool:
        return self._offset * convert.gl_type_to_size(self.data_type) + nbytes > self.size
