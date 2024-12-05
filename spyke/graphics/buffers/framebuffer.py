import dataclasses
import logging

import numpy as np
from OpenGL import GL
from spyke import debug, events, exceptions
from spyke.enums import (FramebufferStatus, MagFilter, MinFilter,
                         SizedInternalFormat, SizedInternalFormatBase,
                         TextureFormat, WrapMode)
from spyke.graphics import opengl_object
from spyke.graphics.opengl_object import OpenglObjectBase
from spyke.graphics.textures import Texture2D, TextureSpec


@dataclasses.dataclass
class AttachmentSpec:
    width: int
    height: int
    texture_format: SizedInternalFormatBase
    min_filter: MinFilter = MinFilter.LinearMipmapLinear
    mag_filter: MagFilter = MagFilter.Linear
    wrap_mode: WrapMode = WrapMode.Repeat
    samples: int = 1

    @property
    def is_depth_attachment(self) -> bool:
        return self.texture_format in [SizedInternalFormat.Depth24Stencil8, SizedInternalFormat.Depth32fStencil8]

    @property
    def is_multisampled(self) -> bool:
        return self.samples > 1

    def to_texture_spec(self) -> TextureSpec:
        return TextureSpec(
            self.width,
            self.height,
            self.texture_format,
            self.samples,
            1,
            self.min_filter,
            self.mag_filter,
            self.wrap_mode)

class Framebuffer(OpenglObjectBase):
    def __init__(self,
                 color_attachments: list[AttachmentSpec],
                 depth_attachment: AttachmentSpec | None = None,
                 use_renderbuffer: bool = False):
        super().__init__()

        if len(color_attachments) > 0:
            self._width = color_attachments[0].width
            self._height = color_attachments[0].height
        else:
            self._width = 0
            self._height = 0

        # TODO: Implement renderbuffers
        if use_renderbuffer:
            _logger.warning('Using renderbuffers as framebuffers attachment is not implemented yet.')

        self._color_attachments = [Texture2D(x.to_texture_spec()) for x in color_attachments]
        self._depth_attachment = Texture2D(depth_attachment.to_texture_spec()) if depth_attachment is not None else None

    @debug.profiled('graphics', 'rendering')
    def bind(self) -> None:
        self.ensure_initialized()
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.id)
        GL.glViewport(0, 0, self._width, self._height)

    @debug.profiled('graphics', 'rendering')
    def unbind(self) -> None:
        self.ensure_initialized()
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    @debug.profiled('graphics', 'buffers', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        GL.glCreateFramebuffers(1, self._id)

        for i, tex in enumerate(self._color_attachments):
            _check_attachment_valid(tex)
            tex.initialize()
            GL.glNamedFramebufferTexture(self.id, GL.GL_COLOR_ATTACHMENT0 + i, tex.id, 0)

        if self._depth_attachment is not None:
            _check_attachment_valid(self._depth_attachment)
            self._depth_attachment.initialize()
            GL.glNamedFramebufferTexture(self.id, GL.GL_DEPTH_STENCIL_ATTACHMENT, tex.id, 0)

        attachments_count = len(self._color_attachments)
        if attachments_count > 0:
            draw_buffers = [GL.GL_COLOR_ATTACHMENT0 + i for i in range(attachments_count)]
            GL.glNamedFramebufferDrawBuffers(self.id, attachments_count, draw_buffers)
        else:
            GL.glNamedFramebufferDrawBuffer(self.id, GL.GL_NONE)

        self._check_complete()

    def get_color_attachment(self, index: int) -> Texture2D:
        assert index < len(self._color_attachments), f'Framebuffer has only {len(self._color_attachments)} color attachments.'
        return self._color_attachments[index]

    def get_depth_attachment(self) -> Texture2D:
        assert self._depth_attachment is not None, 'Framebuffer does not contain depth attachment.'
        return self._depth_attachment

    def read_color_attachment(self, index: int, _format: TextureFormat) -> np.ndarray:
        assert index < len(self._color_attachments), f'Framebuffer has only {len(self._color_attachments)} color attachments.'

        tex = self._color_attachments[index]
        pixels = np.empty((tex.width, tex.height, 3), dtype=np.ubyte)
        GL.glGetTextureSubImage(
            tex.id,
            0,
            0,
            0,
            0,
            tex.width,
            tex.height,
            1,
            _format,
            GL.GL_UNSIGNED_BYTE,
            pixels.nbytes,
            pixels)

        return pixels

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def size(self) -> tuple[int, int]:
        return (self._width, self._height)

    @debug.profiled('graphics', 'cleanup')
    def delete(self) -> None:
        super().delete()

        GL.glDeleteFramebuffers(1, self.id)

    def _check_complete(self) -> None:
        if (status := FramebufferStatus(GL.glCheckNamedFramebufferStatus(self.id, GL.GL_FRAMEBUFFER))) != GL.GL_FRAMEBUFFER_COMPLETE:
            raise exceptions.FramebufferIncompleteException(status)

    @debug.profiled('graphics', 'buffers')
    def resize(self, width: int, height: int) -> None:
        if width == self._width or height == self._height:
            return

        if width == 0 or height == 0:
            return

        self._width = width
        self._height = height

        new_attachments: list[Texture2D] = []
        for tex in self._color_attachments:
            spec = tex.spec
            spec.width = width
            spec.height = height

            opengl_object.delete_object(tex)

            tex = Texture2D(spec)
            tex.initialize()
            new_attachments.append(tex)

        self._color_attachments = new_attachments

        if self._depth_attachment is not None:
            spec = self._depth_attachment.spec
            spec.width = width
            spec.height = height

            opengl_object.delete_object(self._depth_attachment)

            self._depth_attachment = Texture2D(spec)
            self._depth_attachment.initialize()

        _logger.debug('Framebuffer %s resized to (%d, %d).', self, width, height)

def _check_attachment_valid(tex: Texture2D) -> None:
    max_width = GL.glGetInteger(GL.GL_MAX_FRAMEBUFFER_WIDTH)
    max_height = GL.glGetInteger(GL.GL_MAX_FRAMEBUFFER_HEIGHT)
    max_samples = GL.glGetInteger(GL.GL_MAX_FRAMEBUFFER_SAMPLES)

    if tex.width > max_width:
        raise exceptions.GraphicsException(f'Framebuffer attachment ({tex.id}) width is bigger than GL_MAX_FRAMEBUFFER_WIDTH ({max_width}).')

    if tex.height > max_height:
        raise exceptions.GraphicsException(f'Framebuffer attachment ({tex.id}) height is bigger than GL_MAX_FRAMEBUFFER_HEIGHT ({max_height}).')

    if tex.samples > max_samples:
        raise exceptions.GraphicsException(f'Framebuffer attachment ({tex.id}) samples count is higher than GL_MAX_FRAMEBUFFER_SAMPLES ({max_samples}).')

_logger = logging.getLogger(__name__)
