from collections.abc import Buffer as SupportsBufferProtocol

from spyke.graphics import gl


class TextureBuffer:
    def __init__(self,
                 width: int,
                 format: gl.InternalFormat | gl.CompressedInternalFormat,
                 flags: gl.BufferFlag) -> None:
        self.buffer = gl.Buffer(_texture_format_to_size(format) * width, flags)
        self.texture = gl.Texture(
            gl.TextureSpec(
                gl.TextureTarget.TEXTURE_BUFFER,
                width,
                1,
                format,
                min_filter=gl.MinFilter.NEAREST,
                mag_filter=gl.MagFilter.NEAREST))
        self.texture.set_texture_buffer(self.buffer)

    def bind(self, unit: int) -> None:
        self.texture.bind_to_unit(unit)

    def store(self, data: SupportsBufferProtocol) -> None:
        self.buffer.store(data)

    def transfer(self) -> None:
        self.buffer.transfer()

    def reset_offset(self) -> None:
        self.buffer.reset_data_offset()

    def delete(self) -> None:
        self.buffer.delete()
        self.texture.delete()

def _texture_format_to_size(format: gl.InternalFormat | gl.CompressedInternalFormat) -> int:
    match format:
        case gl.InternalFormat.R8:
            return 1
        case gl.InternalFormat.R16:
            return 2
        case gl.InternalFormat.R32F | gl.InternalFormat.R32I | gl.InternalFormat.R32UI:
            return 4
        case gl.InternalFormat.RG8:
            return 2
        case gl.InternalFormat.RG16:
            return 4
        case gl.InternalFormat.RG32F | gl.InternalFormat.RG32I | gl.InternalFormat.RG32UI:
            return 8
        case gl.InternalFormat.RGB8:
            return 3
        case gl.InternalFormat.RGB16:
            return 6
        case gl.InternalFormat.RGB32F | gl.InternalFormat.RGB32I | gl.InternalFormat.RGB32UI:
            return 12
        case gl.InternalFormat.RGBA8:
            return 4
        case gl.InternalFormat.RGBA16:
            return 8
        case gl.InternalFormat.RGBA32F | gl.InternalFormat.RGBA32I | gl.InternalFormat.RGBA32UI:
            return 16
        case unsupported:
            raise ValueError(f'Unsuported format for texture buffer: {unsupported}')
