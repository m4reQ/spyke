from spyke.exceptions import GraphicsException
from .textureSpec import TextureSpec
from .textureData import TextureData
from spyke.enums import MagFilter, MinFilter, TextureFormat, TextureTarget, SizedInternalFormat
from spyke.graphics import gl

from OpenGL import GL
import numpy as np


class Texture(gl.GLObject):
    def __init__(self, tex_data: TextureData, tex_spec: TextureSpec):
        super().__init__()

        self.width: int = tex_data.width
        self.height: int = tex_data.height

        # TODO: Check if texture width and height are less than GL_MAX_TEXTURE_SIZE

        self._id = gl.create_texture(TextureTarget.Texture2d)

        # TODO: Better determine SizedInternalFormat based on type of data that's passed as pixels
        internal_format = tex_spec.internal_format or SizedInternalFormat.Rgba8

        GL.glTextureStorage2D(self.id, tex_spec.mipmaps,
                              internal_format, tex_data.width, tex_data.height)

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

        assert tex_spec.pixel_alignment in [
            1, 2, 4, 8], f'Invalid pixel alignment: {tex_spec.pixel_alignment}'
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, tex_spec.pixel_alignment)

        # TODO: Determine pixel format from tex_data.data.dtype
        GL.glTextureSubImage2D(self.id, 0, 0, 0, tex_data.width,
                               tex_data.height, tex_spec.format, GL.GL_UNSIGNED_BYTE, tex_data.data)
        GL.glGenerateTextureMipmap(self.id)

        success = GL.GLint()
        GL.glGetTextureParameteriv(
            self.id, GL.GL_TEXTURE_IMMUTABLE_FORMAT, success)

        if not success.value:
            raise GraphicsException('Cannot create immutable texture.')

    def bind_to_unit(self, slot) -> None:
        GL.glBindTextureUnit(slot, self.id)

    def delete(self) -> None:
        GL.glDeleteTextures(1, [self.id])

    @classmethod
    def create_white_texture(cls):
        tex_data = TextureData()
        tex_data.data = np.array([255, 255, 255, 255], dtype=np.ubyte)
        tex_data.width = 1
        tex_data.height = 1

        spec = TextureSpec()
        spec.format = TextureFormat.Rgba
        spec.internal_format = SizedInternalFormat.Rgba8
        spec.min_filter = MinFilter.Nearest
        spec.mag_filter = MagFilter.Nearest
        spec.mipmaps = 1

        return cls(tex_data, spec)
