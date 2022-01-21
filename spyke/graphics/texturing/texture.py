from .textureSpec import TextureSpec
from .textureData import TextureData
from spyke.enums import MagFilter, MinFilter, TextureFormat, TextureTarget, SizedInternalFormat
from spyke.graphics import gl
from spyke import debug

from OpenGL import GL
import numpy as np


class Texture(gl.GLObject):
    @debug.timed
    def __init__(self, tex_data: TextureData, tex_spec: TextureSpec):
        super().__init__()

        self.width: int = tex_data.width
        self.height: int = tex_data.height
        self.filepath: str = tex_data.filepath

        self._id = gl.create_texture(TextureTarget.Texture2d)

        # TODO: Determine SizedInternalFormat based on type of data that's passed as pixels
        GL.glTextureStorage2D(self.id, tex_spec.mipmaps,
                              SizedInternalFormat.Rgba8, tex_data.width, tex_data.height)

        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_WRAP_S, tex_spec.wrap_mode)
        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_WRAP_T, tex_spec.wrap_mode)
        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_MIN_FILTER, tex_spec.min_filter)
        GL.glTextureParameteri(
            self.id, GL.GL_TEXTURE_MAG_FILTER, tex_spec.mag_filter)

        GL.glTextureSubImage2D(self.id, 0, 0, 0, tex_data.width,
                               tex_data.height, tex_data.format, GL.GL_UNSIGNED_BYTE, tex_data.data)
        GL.glGenerateTextureMipmap(self.id)

    def bind_to_unit(self, slot) -> None:
        GL.glBindTextureUnit(slot, self.id)

    def delete(self) -> None:
        GL.glDeleteTextures(1, [self.id])

    @classmethod
    def CreateWhiteTexture(cls):
        tex_data = TextureData(1, 1)

        tex_data.data = np.array([255, 255, 255, 255], dtype=np.ubyte)
        tex_data.format = TextureFormat.Rgba

        spec = TextureSpec()
        spec.min_filter = MinFilter.Nearest
        spec.mag_filter = MagFilter.Nearest
        spec.mipmaps = 1
        spec.compress = False

        return cls(tex_data, spec)
