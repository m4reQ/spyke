from __future__ import annotations

import logging
import dataclasses
import typing as t

import numpy as np
from OpenGL import GL
from spyke import debug

from spyke.exceptions import GraphicsException
from spyke.graphics import gl
from spyke.enums import (
    _SizedInternalFormat,
    _CompressedInternalFormat,
    _TextureFormat,
    MinFilter,
    MagFilter,
    WrapMode,
    SizedInternalFormat,
    SwizzleTarget,
    SwizzleMask,
    PixelType,
    TextureFormat,
    TextureParameter,
    TextureTarget,)

_logger = logging.getLogger(__name__)

@dataclasses.dataclass
class TextureSpec:
    width: int = 0
    height: int = 0
    mipmaps: int = 3
    min_filter: MinFilter = MinFilter.LinearMipmapLinear
    mag_filter: MagFilter = MagFilter.Linear
    wrap_mode: WrapMode = WrapMode.Repeat
    texture_swizzle: t.Optional[SwizzleTarget] = None
    internal_format: _SizedInternalFormat = SizedInternalFormat.Rgba8
    _swizzle_mask: t.Optional[np.ndarray] = None

    @property
    def swizzle_mask(self) -> np.ndarray:
        if self._swizzle_mask is not None:
            return self._swizzle_mask
        
        return np.zeros((4,), dtype=np.int32)

    @swizzle_mask.setter
    def swizzle_mask(self, value: t.Sequence[SwizzleMask]) -> None:
        self._swizzle_mask = np.array(value, dtype=np.int32)

class Texture(gl.GLObject):
    _white_texture: t.Optional[Texture] = None
    _invalid_texture: t.Optional[Texture] = None

    @staticmethod
    def set_pixel_alignment(alignment: int) -> None:
        assert alignment in [1, 2, 4, 8], f'Invalid pixel alignment: {alignment}'
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, alignment)

    @classmethod
    def empty(cls):
        '''
        Returns empty white texture of size 1x1,
        creating one if necessary.
        '''

        if cls._white_texture:
            return cls._white_texture

        data = np.array([255, 255, 255, 255], dtype=np.ubyte)

        spec = TextureSpec()
        spec.width = 1
        spec.height = 1
        spec.internal_format = SizedInternalFormat.Rgba8
        spec.min_filter = MinFilter.Nearest
        spec.mag_filter = MagFilter.Nearest
        spec.mipmaps = 1

        tex = cls(spec)
        tex.upload(None, 0, TextureFormat.Rgba, PixelType.UnsignedByte, data)
        tex.check_immutable()

        cls._white_texture = tex
        return cls._white_texture

    @classmethod
    def invalid(cls):
        '''
        Returns texture used to indicate that resource loading
        failed, creating texture if necessary.
        '''

        if cls._invalid_texture:
            return cls._invalid_texture

        data = np.array([
            255, 0, 255, 255,
            0, 0, 0, 255,
            0, 0, 0, 255,
            255, 0, 255, 255], dtype=np.ubyte)

        spec = TextureSpec()
        spec.width = 2
        spec.height = 2
        spec.internal_format = SizedInternalFormat.Rgba8
        spec.min_filter = MinFilter.Nearest
        spec.mag_filter = MagFilter.Nearest
        spec.mipmaps = 1

        tex = cls(spec)
        tex.upload(None, 0, TextureFormat.Rgba, PixelType.UnsignedByte, data)
        tex.check_immutable()

        cls._invalid_texture = tex
        return cls._invalid_texture

    @debug.profiled('graphics', 'textures')
    def __init__(self, specification: TextureSpec):
        super().__init__()

        self.width: int = specification.width
        self.height: int = specification.height
        self.mipmaps: int = specification.mipmaps
        self.is_compressed: bool = isinstance(specification.internal_format, _CompressedInternalFormat)

        # TODO: Check if texture width and height are less than GL_MAX_TEXTURE_SIZE

        self._id = gl.create_texture(TextureTarget.Texture2d)

        GL.glTextureStorage2D(self.id, specification.mipmaps,
                              specification.internal_format, self.width, self.height)

        self.set_parameter(TextureParameter.WrapS, specification.wrap_mode)
        self.set_parameter(TextureParameter.WrapR, specification.wrap_mode)
        self.set_parameter(TextureParameter.WrapT, specification.wrap_mode)
        self.set_parameter(TextureParameter.MinFilter,
                           specification.min_filter)
        self.set_parameter(TextureParameter.MagFilter,
                           specification.mag_filter)
        self.set_parameter(TextureParameter.BaseLevel, 0)
        self.set_parameter(TextureParameter.MaxLevel, self.mipmaps - 1)

        if specification.texture_swizzle:
            assert specification.swizzle_mask is not None, 'Texture swizzle target was set but swizzle mask was not specified'

            GL.glTextureParameteriv(
                self.id, specification.texture_swizzle, specification.swizzle_mask)

        _logger.debug('Texture object with id %d initialized succesfully.', self.id)

    @debug.profiled('graphics', 'textures')
    def upload(self,
               size: t.Optional[tuple[int, int]],
               level: int,
               _format: _TextureFormat,
               pixel_type: PixelType,
               data: np.ndarray) -> None:
        assert not self.is_compressed, 'Cannot use Texture.upload on compressed texture. Use Texture.upload_compressed instead.'

        # TODO: Add check for weird texture conversion from formats that differ much
        # i.e. GL.GL_RG8 <= GL.GL_RGBA
        if size is None:
            size = (self.width, self.height)

        GL.glTextureSubImage2D(self.id, level, 0, 0, *size, _format, pixel_type, data)

        _logger.debug('Texture data of size (%d, %d) uploaded to texture object %d as level %d.', size[0], size[1], self.id, level)

    @debug.profiled('graphics', 'textures')
    def upload_compressed(self,
                          size: t.Optional[tuple[int, int]],
                          level: int,
                          _format: _TextureFormat,
                          image_size: int,
                          data: np.ndarray) -> None:
        assert self.is_compressed, 'Cannot use Texture.upload_compressed on non-compressed texture. Use Texture.upload instead.'

        if size is None:
            size = (self.width, self.height)

        GL.glCompressedTextureSubImage2D(self.id, level, 0, 0, *size, _format, image_size, data)

        _logger.debug('Compressed texture data of size (%d, %d) uploaded to texture object %d as level %d. Texture format: %s', size[0], size[1], self.id, level, _format.name)

    def set_parameter(self, parameter: TextureParameter, value: t.Any) -> None:
        GL.glTextureParameteri(self.id, parameter, value)

    @debug.profiled('graphics', 'textures')
    def generate_mipmap(self) -> None:
        GL.glGenerateTextureMipmap(self.id)

    def bind_to_unit(self, slot) -> None:
        GL.glBindTextureUnit(slot, self.id)

    @debug.profiled('graphics', 'textures')
    def _delete(self) -> None:
        GL.glDeleteTextures(1, [self.id])

    def check_immutable(self) -> None:
        success = GL.GLint()
        GL.glGetTextureParameteriv(self.id, GL.GL_TEXTURE_IMMUTABLE_FORMAT, success)

        if success.value != 1:
            raise GraphicsException('Cannot create immutable texture.')
