from __future__ import annotations
from spyke.exceptions import GraphicsException
from .textureSpec import TextureSpec
from spyke.enums import _CompressedInternalFormat, MagFilter, MinFilter, PixelType, _TextureFormat, TextureFormat, TextureParameter, TextureTarget, SizedInternalFormat
from spyke.graphics import gl
from typing import Any, Optional, Tuple, Union
from OpenGL import GL
import numpy as np
import logging

_LOGGER = logging.getLogger(__name__)

class Texture(gl.GLObject):
    _white_texture: Optional[Texture] = None
    _invalid_texture: Optional[Texture] = None

    @staticmethod
    def set_pixel_alignment(alignment: int) -> None:
        assert alignment in [
            1, 2, 4, 8], f'Invalid pixel alignment: {alignment}'
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
        tex._check_immutable()

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
        tex._check_immutable()

        cls._invalid_texture = tex
        return cls._invalid_texture

    def __init__(self, specification: TextureSpec):
        super().__init__()

        self.width: int = specification.width
        self.height: int = specification.height
        self.mipmaps: int = specification.mipmaps
        self.is_compressed: bool = isinstance(
            specification.internal_format, _CompressedInternalFormat)

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
        
        _LOGGER.debug('Texture object with id %d initialized succesfully.', self.id)

    def upload(self, size: Optional[Tuple[int, int]], level: int, _format: _TextureFormat, pixel_type: PixelType, data: np.ndarray) -> None:
        assert not self.is_compressed, 'Cannot use Texture.upload on compressed texture. Use Texture.upload_compressed instead.'

        # TODO: Add check for weird texture conversion from formats that differ much
        # i.e. GL.GL_RG8 <= GL.GL_RGBA
        if size is None:
            size = (self.width, self.height)

        GL.glTextureSubImage2D(self.id, level, 0, 0, *size, _format, pixel_type, data)

        _LOGGER.debug('Texture data of size (%d, %d) uploaded to texture object %d as level %d.', size[0], size[1], self.id, level)

    def upload_compressed(self, size: Union[Tuple[int, int], None], level: int, _format: _TextureFormat, image_size: int, data: np.ndarray) -> None:
        assert self.is_compressed, 'Cannot use Texture.upload_compressed on non-compressed texture. Use Texture.upload instead.'

        if size is None:
            size = (self.width, self.height)

        GL.glCompressedTextureSubImage2D(self.id, level, 0, 0, size[0], size[1], format, image_size, data)
        
        _LOGGER.debug('Compressed texture data of size (%d, %d) uploaded to texture object %d as level %d. Texture format: %s', size[0], size[1], self.id, level, _format.name)

    def set_parameter(self, parameter: TextureParameter, value: Any) -> None:
        GL.glTextureParameteri(self.id, parameter, value)

    def generate_mipmap(self) -> None:
        GL.glGenerateTextureMipmap(self.id)

    def bind_to_unit(self, slot) -> None:
        GL.glBindTextureUnit(slot, self.id)

    def _delete(self) -> None:
        GL.glDeleteTextures(1, [self.id])

    def _check_immutable(self) -> None:
        success = GL.GLint()
        GL.glGetTextureParameteriv(
            self.id, GL.GL_TEXTURE_IMMUTABLE_FORMAT, success)

        if success.value != 1:
            raise GraphicsException('Cannot create immutable texture.')