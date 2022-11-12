import typing as t

import numpy as np
import numpy.typing as npt
from OpenGL import GL

from spyke import debug, exceptions
from spyke.enums import (SizedInternalFormat, TextureBufferSizedInternalFormat,
                         TextureTarget)
from spyke.graphics.textures import TextureBase, TextureSpec, TextureUploadData

from .dynamic_buffer import DynamicBuffer


class _TextureBufferTexture(TextureBase):
    def __init__(self, spec: TextureSpec) -> None:
        super().__init__(TextureTarget.TextureBuffer, spec, False)

    def create_storage(self) -> None:
        pass

    def upload(self, data: TextureUploadData, generate_mipmap: bool = True) -> None:
        raise exceptions.GraphicsException('Cannot use upload on buffer texture.')

    def upload_compressed(self, data: TextureUploadData, generate_mipmap: bool = True) -> None:
        raise exceptions.GraphicsException('Cannot use upload_compressed on buffer texture.')

    def _check_is_immutable(self) -> None:
        pass

class TextureBuffer(DynamicBuffer):
    def __init__(self, count: int, internal_format: TextureBufferSizedInternalFormat, dtype: npt.DTypeLike = np.float32) -> None:
        super().__init__(count, dtype)

        self._internal_format = internal_format
        self._texture = _TextureBufferTexture(TextureSpec(count, 1, t.cast(SizedInternalFormat, internal_format), mipmaps=1))

    @debug.profiled('graphics', 'buffers', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        self._texture.initialize()
        GL.glTextureBuffer(self._texture.id, self._internal_format, self.id)

    @debug.profiled('graphics', 'rendering')
    def bind(self, tex_unit: int) -> None:
        GL.glBindTextureUnit(tex_unit, self._texture.id)

    @property
    def texture(self) -> _TextureBufferTexture:
        return self._texture
