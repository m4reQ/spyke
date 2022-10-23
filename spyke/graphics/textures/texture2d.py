import logging
import typing as t

from OpenGL import GL
from spyke import debug
from spyke.enums import TextureTarget

from .texture import TextureBase
from .texture_spec import TextureSpec
from .upload_data import TextureUploadData


@t.final
class Texture2D(TextureBase):
    def __init__(self, spec: TextureSpec, use_parameters: bool = True) -> None:
        super().__init__(TextureTarget.Texture2d, spec, use_parameters)

    @debug.profiled('graphics', 'textures', 'initialization')
    def create_storage(self) -> None:
        if self.spec.is_multisampled:
            GL.glTextureStorage2DMultisample(self.id, self.spec.samples, self.internal_format, self.width, self.height, True)
        else:
            GL.glTextureStorage2D(self.id, self.mipmaps, self.internal_format, self.width, self.height)

        _logger.debug('Storage for texture object with id %d allocated succesfully.', self.id)

    @debug.profiled('graphics', 'textures')
    def upload(self, data: TextureUploadData, generate_mipmap: bool = True) -> None:
        self.ensure_initialized()

        GL.glTextureSubImage2D(self.id, data.level, 0, 0, data.width, data.height, data.format, data.pixel_type, data.data)
        if generate_mipmap and self.mipmaps > 1:
            self.generate_mipmap()

        _logger.debug(
            'Texture data of size (%d, %d) uploaded to texture object %d as level %d. Texture format: %s',
            data.width,
            data.height,
            self.id,
            data.level,
            data.format.name)

    @debug.profiled('graphics', 'textures')
    def upload_compressed(self, data: TextureUploadData, generate_mipmap: bool = False) -> None:
        assert data.image_size != 0, 'image_size property has to be non-zero when using TextureUploadData with upload_compressed'
        self.ensure_initialized()

        GL.glCompressedTextureSubImage2D(self.id, data.level, 0, 0, data.width, data.height, data.format, data.image_size, data.data)
        if generate_mipmap and self.mipmaps > 1:
            self.generate_mipmap()

        _logger.debug(
            'Compressed texture data of size (%d, %d) uploaded to texture object %d as level %d. Texture format: %s',
            data.width,
            data.height,
            self.id,
            data.level,
            data.format.name)

_logger = logging.getLogger(__name__)
