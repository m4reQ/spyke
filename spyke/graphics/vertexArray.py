from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.graphics.buffers import Buffer
    from spyke.enums import GLType

import logging
from spyke.graphics import gl
from spyke.utils import convert

from OpenGL import GL


class VertexArray(gl.GLObject):
    def __init__(self):
        super().__init__()

        self._id = gl.create_vertex_array()

        self._offsets = {}

        logging.log(logging.SP_INFO, f'{self} created succesfully.')

    def bind_vertex_buffer(self, binding_index: int, buffer: Buffer, offset: int, stride: int) -> None:
        GL.glVertexArrayVertexBuffer(
            self.id, binding_index, buffer.id, offset, stride)

    def bind_element_buffer(self, buffer: Buffer) -> None:
        GL.glVertexArrayElementBuffer(self.id, buffer.id)

    def add_layout(self, attrib_index: int, binding_index: int, count: int, _type: GLType, is_normalized: bool, divisor: int = 0) -> None:
        if binding_index in self._offsets:
            offset = self._offsets[binding_index]
        else:
            offset = 0
            self._offsets[binding_index] = 0

        GL.glEnableVertexArrayAttrib(self.id, attrib_index)
        GL.glVertexArrayAttribFormat(
            self.id, attrib_index, count, _type, is_normalized, offset)
        GL.glVertexArrayBindingDivisor(self.id, binding_index, divisor)
        GL.glVertexArrayAttribBinding(self.id, attrib_index, binding_index)

        self._offsets[binding_index] += convert.gl_type_to_size(_type) * count

    def add_matrix_layout(self, attrib_index: int, binding_index: int, cols: int, rows: int, _type: GLType, is_normalized: bool, divisor: int = 0) -> None:
        for i in range(rows):
            self.add_layout(attrib_index + i, binding_index,
                            cols, _type, is_normalized, divisor)

    def bind(self) -> None:
        GL.glBindVertexArray(self.id)

    def _delete(self) -> None:
        GL.glDeleteVertexArrays(1, [self.id])
