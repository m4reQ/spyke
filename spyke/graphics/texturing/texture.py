from __future__ import annotations
from spyke.exceptions import GraphicsException
from .textureSpec import TextureSpec
from spyke.enums import MagFilter, MinFilter, PixelType, TextureFormat, TextureTarget, SizedInternalFormat
from spyke.graphics import gl
from typing import Tuple, Union

from OpenGL import GL
import numpy as np


class Texture(gl.GLObject):
    @staticmethod
    def set_pixel_alignment(alignment: int) -> None:
        assert alignment in [
            1, 2, 4, 8], f'Invalid pixel alignment: {alignment}'
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, alignment)

    def __init__(self, tex_spec: TextureSpec):
        super().__init__()

        self.width: int = tex_spec.width
        self.height: int = tex_spec.height
        self.mipmaps: int = tex_spec.mipmaps

        # TODO: Check if texture width and height are less than GL_MAX_TEXTURE_SIZE

        self._id = gl.create_texture(TextureTarget.Texture2d)

        GL.glTextureStorage2D(self.id, tex_spec.mipmaps,
                              tex_spec.internal_format, self.width, self.height)

        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_WRAP_S, tex_spec.wrap_mode)
        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_WRAP_T, tex_spec.wrap_mode)
        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_WRAP_R, tex_spec.wrap_mode)
        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_MIN_FILTER, tex_spec.min_filter)
        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_MAG_FILTER, tex_spec.mag_filter)

        if tex_spec.texture_swizzle:
            assert tex_spec.swizzle_mask is not None, 'Texture swizzle target was set but swizzle mask was not specified'

            GL.glTextureParameteriv(
                self.id, tex_spec.texture_swizzle, tex_spec.swizzle_mask)

    def upload(self, size: Union[Tuple[int, int], None], level: int, format: TextureFormat, pixel_type: PixelType, data: np.ndarray) -> None:
        # TODO: Add check for weird texture conversion from formats that differ much
        # i.e. GL.GL_RG8 <= GL.GL_RGBA
        if size is None:
            size = (self.width, self.height)

        GL.glTextureSubImage2D(self.id, level, 0, 0,
                               size[0], size[1], format, pixel_type, data)

    def generate_mipmap(self) -> None:
        GL.glGenerateTextureMipmap(self.id)

    def bind_to_unit(self, slot) -> None:
        GL.glBindTextureUnit(slot, self.id)

    def delete(self) -> None:
        GL.glDeleteTextures(1, [self.id])

    def _check_immutable(self) -> None:
        success = GL.GLint()
        GL.glGetTextureParameteriv(
            self.id, GL.GL_TEXTURE_IMMUTABLE_FORMAT, success)

        if success.value != 1:
            raise GraphicsException('Cannot create immutable texture.')

    @classmethod
    def create_white_texture(cls):
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

        return tex
