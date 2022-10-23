import typing as t

import numpy as np
import numpy.typing as npt
from OpenGL import GL
from spyke import debug
from spyke.enums import SizedInternalFormat, TextureBufferSizedInternalFormat
from spyke.graphics.textures import Texture2D, TextureSpec

from .dynamic_buffer import DynamicBuffer


class TextureBuffer(DynamicBuffer):
    def __init__(self, count: int, internal_format: TextureBufferSizedInternalFormat, dtype: npt.DTypeLike = np.float32) -> None:
        super().__init__(count, dtype)

        self._internal_format = internal_format
        self._texture = Texture2D(TextureSpec(count, 1, t.cast(SizedInternalFormat, internal_format), mipmaps=1), False)

    @debug.profiled('graphics', 'buffers', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        self._texture.initialize()
        GL.glTextureBuffer(self._texture.id, self._internal_format, self.id)

    @property
    def texture(self) -> Texture2D:
        return self._texture
