from __future__ import annotations

import abc
import typing as t

import numpy as np
from OpenGL import GL
from spyke import debug, exceptions
from spyke.enums import SizedInternalFormat, TextureParameter, TextureTarget
from spyke.graphics.opengl_object import OpenglObjectBase

from .texture_spec import TextureSpec
from .upload_data import TextureUploadData


class TextureBase(OpenglObjectBase, abc.ABC):
    @debug.profiled('graphics', 'textures', 'rendering')
    @staticmethod
    def bind_textures(first: int, textures: t.Sequence[TextureBase]) -> None:
        GL.glBindTextures(first, len(textures), [x.id for x in textures])

    @staticmethod
    def set_pixel_unpack_alignment(alignment: t.Literal[1, 2, 4, 8]) -> None:
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, alignment)

    @staticmethod
    def set_pixel_pack_alignment(alignment: t.Literal[1, 2, 4, 8]) -> None:
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, alignment)

    def __init__(self, target: TextureTarget, spec: TextureSpec, use_parameters: bool) -> None:
        super().__init__()

        self._target = target
        self._spec = spec
        self._use_parameters = use_parameters

    @debug.profiled('graphics', 'textures', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        self._check_valid_size()

        GL.glCreateTextures(self._target, 1, self._id)

        self.create_storage()

        if self._use_parameters:
            GL.glTextureParameteri(self.id, TextureParameter.WrapS, self._spec.wrap_mode)
            GL.glTextureParameteri(self.id, TextureParameter.WrapR, self._spec.wrap_mode)
            GL.glTextureParameteri(self.id, TextureParameter.WrapT, self._spec.wrap_mode)
            GL.glTextureParameteri(self.id, TextureParameter.MinFilter, self._spec.min_filter)
            GL.glTextureParameteri(self.id, TextureParameter.MagFilter, self._spec.mag_filter)
            GL.glTextureParameteri(self.id, TextureParameter.MaxLevel, 1 if self._spec.is_multisampled else self._spec.mipmaps - 1)
            GL.glTextureParameteri(self.id, TextureParameter.BaseLevel, 0)
            if self._spec.swizzle_mask:
                GL.glTextureParameteriv(self.id, self._spec.texture_swizzle, np.asarray(self._spec.swizzle_mask, dtype=np.uint))

        self._check_is_immutable()

    @debug.profiled('graphics', 'cleanup')
    def delete(self) -> None:
        super().delete()

        GL.glDeleteTextures(1, self._id)

    def set_parameter(self, parameter: TextureParameter, value: int | list[t.SupportsInt]) -> None:
        self.ensure_initialized()

        if isinstance(value, int):
            GL.glTextureParameteri(self.id, parameter, value)
        else:
            GL.glTextureParameteriv(self.id, parameter, np.asarray(value, dtype=np.int32))

    @debug.profiled('graphics', 'textures')
    def generate_mipmap(self) -> None:
        self.ensure_initialized()

        GL.glGenerateTextureMipmap(self.id)

    @debug.profiled('graphics', 'textures', 'rendering')
    def bind_to_unit(self, slot: int) -> None:
        self.ensure_initialized()

        GL.glBindTextureUnit(slot, self.id)

    @abc.abstractmethod
    def create_storage(self) -> None:
        pass

    @abc.abstractmethod
    def upload(self, data: TextureUploadData, generate_mipmap: bool) -> None:
        pass

    @abc.abstractmethod
    def upload_compressed(self, data: TextureUploadData, generate_mipmap: bool) -> None:
        pass

    @property
    def width(self) -> int:
        return self._spec.width

    @property
    def height(self) -> int:
        return self._spec.height

    @property
    def internal_format(self) -> SizedInternalFormat:
        return self._spec.internal_format

    @property
    def spec(self) -> TextureSpec:
        return self._spec

    @property
    def mipmaps(self) -> int:
        return self._spec.mipmaps

    @property
    def samples(self) -> int:
        return self._spec.samples

    def _check_is_immutable(self) -> None:
        success = GL.GLint()
        GL.glGetTextureParameteriv(self.id, GL.GL_TEXTURE_IMMUTABLE_FORMAT, success)

        if success.value != 1:
            raise exceptions.GraphicsException(f'Couldn\'t create immutable texture {self}.')

    def _check_valid_size(self):
        max_size = GL.glGetInteger(GL.GL_MAX_TEXTURE_SIZE)
        if self._spec.width >= max_size or self._spec.height >= max_size:
            raise exceptions.GraphicsException(f'Texture size too big: ({self._spec.width}, {self._spec.height}). Max side length is: {max_size}.')
