from spyke.enums import MinFilter, TextureFormat, TextureTarget
from spyke.graphics import gl
from spyke import debug

from OpenGL import GL
import numpy as np
import typing

if typing.TYPE_CHECKING:
    from spyke.graphics.texturing import TextureSpec, TextureData
    from spyke.enums import SizedInternalFormat


class Texture(gl.GLObject):
    @debug.timed
    def __init__(self, tex_data: TextureData, tex_spec: TextureSpec, internal_format: SizedInternalFormat):
        super().__init__()

        self.width: int = tex_data.width
        self.height: int = tex_data.height
        self.filepath: str = tex_data.filepath

        self._id = gl.create_texture(TextureTarget.Texture2d)

        GL.glTextureStorage2D(self.id, tex_spec.mipmaps,
                              internal_format, tex_data.width, tex_data.height)

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
        spec.mag_filter = MinFilter.Nearest
        spec.mipmaps = 1
        spec.compress = False

        return cls(tex_data, spec, SizedInternalFormat.Rgba8)
