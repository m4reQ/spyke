import typing as t

from pygl import buffers, textures


class TextureBuffer:
    def __init__(self,
                 width: int,
                 format: textures.InternalFormat | textures.CompressedInternalFormat,
                 flags: buffers.BufferFlags) -> None:
        self.buffer = buffers.Buffer(
            _texture_format_to_size(format) * width,
            flags)
        self.texture = textures.Texture(
            textures.TextureSpec(
                textures.TextureTarget.TEXTURE_BUFFER,
                width,
                1,
                format,
                min_filter=textures.MinFilter.NEAREST,
                mag_filter=textures.MagFilter.NEAREST))

        self.texture.set_texture_buffer(self.buffer)

    def bind(self, unit: int) -> None:
        self.texture.bind_to_unit(unit)

    # TODO Fix typing in `TextureBuffer.store`
    def store(self, data: t.Any) -> None:
        self.buffer.store(data)

    def transfer(self) -> None:
        self.buffer.transfer()

    def reset_offset(self) -> None:
        self.buffer.reset_offset()

    def delete(self) -> None:
        self.buffer.delete()
        self.texture.delete()

def _texture_format_to_size(format: textures.InternalFormat | textures.CompressedInternalFormat) -> int:
    match format:
        case textures.InternalFormat.R8:
            return 1
        case textures.InternalFormat.R16:
            return 2
        case textures.InternalFormat.R32F | textures.InternalFormat.R32I | textures.InternalFormat.R32UI:
            return 4

        case textures.InternalFormat.RG8:
            return 2
        case textures.InternalFormat.RG16:
            return 4
        case textures.InternalFormat.RG32F | textures.InternalFormat.RG32I | textures.InternalFormat.RG32UI:
            return 8

        case textures.InternalFormat.RGB8:
            return 3
        case textures.InternalFormat.RGB16:
            return 6
        case textures.InternalFormat.RGB32F | textures.InternalFormat.RGB32I | textures.InternalFormat.RGB32UI:
            return 12

        case textures.InternalFormat.RGBA8:
            return 4
        case textures.InternalFormat.RGBA16:
            return 8
        case textures.InternalFormat.RGBA32F | textures.InternalFormat.RGBA32I | textures.InternalFormat.RGBA32UI:
            return 16

        case unsupported:
            raise ValueError(f'Unsuported format for texture buffer: {unsupported}')
