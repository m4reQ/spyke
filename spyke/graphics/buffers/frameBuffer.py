import dataclasses
import logging
import typing as t

from OpenGL import GL
from spyke import debug, events, exceptions
from spyke.enums import (AttachmentPoint, FramebufferStatus, MagFilter,
                         MinFilter, SizedInternalFormat,
                         SizedInternalFormatBase, WrapMode)
from spyke.graphics.opengl_object import OpenglObjectBase
from spyke.graphics.textures import Texture2D, TextureSpec


@dataclasses.dataclass
class AttachmentSpec:
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

    def as_texture_spec(self, width: int, height: int) -> TextureSpec:
        return TextureSpec(
            width=width,
            height=height,
            mipmaps=1,
            samples=self.samples,
            min_filter=self.min_filter,
            mag_filter=self.mag_filter,
            wrap_mode=self.wrap_mode,
            internal_format=self.texture_format)

@dataclasses.dataclass
class FramebufferSpec:
    width: int
    height: int
    is_resizable: bool = False
    attachments_specs: list[AttachmentSpec] = dataclasses.field(default_factory=list)

class Framebuffer(OpenglObjectBase):
    def __init__(self, spec: FramebufferSpec):
        super().__init__()

        self._width = spec.width
        self._height = spec.height
        self._is_resizable = spec.is_resizable

        self._color_attachments, self._depth_attachment = _create_framebuffer_attachments(spec.attachments_specs, spec.width, spec.height)

        if spec.is_resizable:
            events.register(
                self._resize_callback,
                events.ResizeEvent,
                priority=-2)

    @debug.profiled('graphics')
    def bind(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.id)
        GL.glViewport(0, 0, self._width, self._height)

    @debug.profiled('graphics')
    def unbind(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def get_color_attachment(self, index: int) -> Texture2D:
        assert index < len(self._color_attachments), f'Framebuffer has only {len(self._color_attachments)} color attachments.'
        return self._color_attachments[index]

    def get_depth_attachment(self) -> Texture2D:
        assert self._depth_attachment is not None, 'Framebuffer does not contain depth attachment.'
        return self._depth_attachment

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @debug.profiled('graphics', 'initialization')
    def _initialize(self, context: t.Any) -> None:
        GL.glCreateFramebuffers(1, self._id)

        max_attachments = context.get_integer(GL.GL_MAX_COLOR_ATTACHMENTS)
        attachments_count = len(self._color_attachments)
        if attachments_count > max_attachments:
            raise exceptions.GraphicsException(f'Cannot attach more than {max_attachments} color attachments to a single framebuffer.')

        for i, tex in enumerate(self._color_attachments):
            tex.initialize()
            _check_attachment_valid(tex, context)
            self._attach_texture(tex, _get_attachment_point(tex.internal_format), i)

        if self._depth_attachment:
            self._depth_attachment.initialize()
            _check_attachment_valid(self._depth_attachment, context)
            self._attach_texture(self._depth_attachment, _get_attachment_point(self._depth_attachment.internal_format))

        if attachments_count == 0:
            GL.glNamedFramebufferDrawBuffer(self.id, GL.GL_NONE)
        else:
            draw_buffers = [AttachmentPoint.ColorAttachment + i for i in range(attachments_count)]
            GL.glNamedFramebufferDrawBuffers(
                self.id,
                attachments_count,
                draw_buffers)

        self._check_complete()

    @debug.profiled('graphics', 'cleanup')
    def _dispose(self) -> None:
        self._delete_attachments()

        GL.glDeleteFramebuffers(1, self._id)

    @debug.profiled('graphics', 'cleanup')
    def _delete_attachments(self) -> None:
        for tex in self._color_attachments:
            tex.dispose()

        self._color_attachments.clear()

        if self._depth_attachment:
            self._depth_attachment.dispose()
            self._depth_attachment = None

    def _attach_texture(self, texture: Texture2D, attachment_point: AttachmentPoint, index: int=0) -> None:
        attachment: int
        if attachment_point == AttachmentPoint.ColorAttachment:
            attachment = attachment_point + index
        else:
            attachment = attachment_point

        GL.glNamedFramebufferTexture(self.id, attachment, texture.id, 0)

    def _check_complete(self) -> None:
        status = FramebufferStatus(GL.glCheckNamedFramebufferStatus(self.id, GL.GL_FRAMEBUFFER))
        if status != FramebufferStatus.Complete:
            raise exceptions.FramebufferIncompleteException(status)

    def _resize_callback(self, e: events.ResizeEvent) -> None:
        if not self._is_resizable:
            raise exceptions.GraphicsException('Tried to resize framebuffer that is marked as non-resizable.')

        if e.width == 0 or e.height == 0:
            return

        self._width = e.width
        self._height = e.height

        self._dispose()

        ctx = gl.context.get_current()
        self._initialize(ctx)

        _logger.debug('Framebuffer %s resized to (%d, %d).', self, e.width, e.height)

def _get_attachment_point(internal_format: SizedInternalFormatBase) -> AttachmentPoint:
    match internal_format:
        case SizedInternalFormat.DepthComponent16 | SizedInternalFormat.DepthComponent24 | SizedInternalFormat.DepthComponent32f:
            return AttachmentPoint.DepthAttachment
        case SizedInternalFormat.Depth24Stencil8 | SizedInternalFormat.Depth32fStencil8:
            return AttachmentPoint.DepthStencilAttachment
        case SizedInternalFormat.StencilIndex8:
            return AttachmentPoint.StencilAttachment

    return AttachmentPoint.ColorAttachment

def _create_framebuffer_attachments(specs: list[AttachmentSpec], width: int, height: int) -> tuple[list[Texture2D], Texture2D | None]:
    color_attachments = [Texture2D(x.as_texture_spec(width, height)) for x in specs if not x.is_depth_attachment]

    depth_spec = next((x for x in specs if x.is_depth_attachment), None)
    depth_attachment: Texture2D | None = None
    if depth_spec:
        depth_attachment = Texture2D(depth_spec.as_texture_spec(width, height))

    return (color_attachments, depth_attachment)

def _check_attachment_valid(tex: Texture2D, ctx: t.Any) -> None:
    max_width = ctx.get_integer(GL.GL_MAX_FRAMEBUFFER_WIDTH)
    max_height = ctx.get_integer(GL.GL_MAX_FRAMEBUFFER_HEIGHT)
    max_samples = ctx.get_integer(GL.GL_MAX_FRAMEBUFFER_SAMPLES)

    if tex.width > max_width:
        raise exceptions.GraphicsException(f'Framebuffer attachment ({tex.id}) width is bigger than GL_MAX_FRAMEBUFFER_WIDTH ({max_width}).')

    if tex.height > max_height:
        raise exceptions.GraphicsException(f'Framebuffer attachment ({tex.id}) height is bigger than GL_MAX_FRAMEBUFFER_HEIGHT ({max_height}).')

    if tex.samples > max_samples:
        raise exceptions.GraphicsException(f'Framebuffer attachment ({tex.id}) samples count is higher than GL_MAX_FRAMEBUFFER_SAMPLES ({max_samples}).')

_logger = logging.getLogger(__name__)
