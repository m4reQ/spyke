import ctypes as ct
from collections import defaultdict

from OpenGL import GL

from spyke import debug
from spyke.enums import GLType
from spyke.graphics.buffers import BufferBase
from spyke.graphics.opengl_object import OpenglObjectBase
from spyke.utils import convert


class VertexArray(OpenglObjectBase):
    def __init__(self):
        super().__init__()

        self._offsets = defaultdict[int, int](lambda: 0)

    @debug.profiled('graphics', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        GL.glCreateVertexArrays(1, ct.pointer(self._id))

    @debug.profiled('graphics', 'cleanup')
    def delete(self) -> None:
        super().delete()

        GL.glDeleteVertexArrays(1, ct.pointer(self._id))

    @debug.profiled('graphics', 'setup')
    def bind_vertex_buffer(self, binding_index: int, buffer: BufferBase, offset: int, stride: int, divisor: int = 0) -> None:
        self.ensure_initialized()
        buffer.ensure_initialized()

        GL.glVertexArrayVertexBuffer(
            self.id,
            binding_index,
            buffer.id,
            offset,
            stride)
        GL.glVertexArrayBindingDivisor(self.id, binding_index, divisor)

    @debug.profiled('graphics', 'setup')
    def bind_element_buffer(self, buffer: BufferBase) -> None:
        self.ensure_initialized()
        buffer.ensure_initialized()

        GL.glVertexArrayElementBuffer(self.id, buffer.id)

    @debug.profiled('graphics', 'setup')
    def add_layout(self, attrib_index: int, binding_index: int, count: int, _type: GLType, is_normalized: bool = False) -> None:
        self.ensure_initialized()

        GL.glEnableVertexArrayAttrib(self.id, attrib_index)
        GL.glVertexArrayAttribFormat(
            self.id,
            attrib_index,
            count,
            _type,
            is_normalized,
            self._offsets[binding_index])

        GL.glVertexArrayAttribBinding(self.id, attrib_index, binding_index)

        self._offsets[binding_index] += convert.gl_type_to_size(_type) * count

    @debug.profiled('graphics', 'setup')
    def add_matrix_layout(self, attrib_index: int, binding_index: int, cols: int, rows: int, _type: GLType, is_normalized: bool = False) -> None:
        for i in range(rows):
            self.add_layout(
                attrib_index + i,
                binding_index,
                cols,
                _type,
                is_normalized)

    @debug.profiled('graphics', 'rendering')
    def bind(self) -> None:
        self.ensure_initialized()
        GL.glBindVertexArray(self.id)
