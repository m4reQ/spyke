from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.enums import GLType, InternalFormat

from spyke.graphics import gl
from spyke.enums import TextureTarget
from .buffer import DynamicBuffer

from OpenGL import GL


class TextureBuffer(DynamicBuffer):
    def __init__(self, size: int, data_type: GLType, format: InternalFormat):
        super().__init__(size, data_type)

        self._tex_id = gl.create_texture(TextureTarget.TextureBuffer)
        GL.glTextureBuffer(self.texture_id, format, self.id)

    def delete(self) -> None:
        super().delete()
        GL.glDeleteTextures(1, [self.texture_id])

    @property
    def texture_id(self) -> int:
        return self._tex_id.value
