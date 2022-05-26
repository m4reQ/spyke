import dataclasses
import logging
import typing as t

from OpenGL import GL

from spyke import events
from spyke.graphics import gl
from spyke.graphics.texturing.texture_proxy import TextureProxy
from spyke.exceptions import GraphicsException
from spyke.enums import (
    AttachmentPoint,
    FramebufferStatus,
    MagFilter,
    MinFilter,
    SizedInternalFormat,
    TextureFormat,
    TextureParameter,
    TextureTarget,
    WrapMode)

_logger = logging.getLogger(__name__)

@dataclasses.dataclass
class AttachmentSpec:
    texture_format: SizedInternalFormat
    min_filter: MinFilter = MinFilter.LinearMipmapLinear
    mag_filter: MagFilter = MagFilter.Linear
    wrap_mode: WrapMode = WrapMode.Repeat

    @property
    def attachment_point(self) -> AttachmentPoint:
        if self.texture_format in [
            SizedInternalFormat.DepthComponent16,
            SizedInternalFormat.DepthComponent24,
            SizedInternalFormat.DepthComponent32f]:
            return AttachmentPoint.DepthAttachment
        
        if self.texture_format in [
            SizedInternalFormat.Depth24Stencil8,
            SizedInternalFormat.Depth32fStencil8]:
            return AttachmentPoint.DepthStencilAttachment
        
        if self.texture_format == SizedInternalFormat.StencilIndex8:
            return AttachmentPoint.StencilAttachment
        
        return AttachmentPoint.ColorAttachment

@dataclasses.dataclass
class FramebufferSpec:
    width: int
    height: int
    samples: int = 1
    is_resizable: bool = False
    attachments_specs: t.List[AttachmentSpec] = dataclasses.field(default_factory=list)

# TODO: Maybe its worth creating separate class `FramebufferAttachment` which will store all
# informations about attachment as well as the created texture id together

# TODO: Add support for attachments of various sizes

class Framebuffer(gl.GLObject):
    def __init__(self, specification: FramebufferSpec):
        super().__init__()

        self._id = gl.create_framebuffer()

        self.width = specification.width
        self.height = specification.height

        self.specification: FramebufferSpec = specification

        self.color_attachment_specs: t.List[AttachmentSpec] = []
        self.depth_attachment_spec: t.Optional[AttachmentSpec] = None

        self._get_attachments_specs(specification)

        self.color_attachments: t.List[int] = []
        self.depth_attachment: int = 0

        self._invalidate(True)

        if specification.is_resizable:
            events.register(
                self._resize_callback,
                events.ResizeEvent,
                priority=-2)

        _logger.debug('%s created succesfully.', self)

    def bind(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.id)
        GL.glViewport(0, 0, self.width, self.height)

    def unbind(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def resize(self, width: int, height: int) -> None:
        if not self.specification.is_resizable:
            raise GraphicsException(
                'Tried to resize framebuffer that is marked as non-resizable.')

        self.width = width
        self.height = height

        self._invalidate(False)

        _logger.debug('%s resized to (%d, %d).', self, width, height)

    def _delete(self) -> None:
        GL.glDeleteFramebuffers(1, [self.id])
        GL.glDeleteTextures(
            len(self.color_attachments) + 1,
            self.color_attachments + [self.depth_attachment])

        self.color_attachments.clear()
        self.depth_attachment = 0

    def get_color_attachment(self, index: int) -> TextureProxy:
        max_index = len(self.color_attachments) - 1
        if index > max_index:
            raise GraphicsException(
                f'Cannot get framebuffer color attachment with index {index}. Max index is {max_index}.')

        return TextureProxy(self.color_attachments[index])

    def get_depth_attachment(self) -> int:
        if not self.depth_attachment:
            raise GraphicsException(
                'Framebuffer does not contain depth attachment.')

        return self.depth_attachment

    def _get_attachments_specs(self, specification: FramebufferSpec) -> None:
        for attachment_spec in specification.attachments_specs:
            if attachment_spec.texture_format in [TextureFormat.DepthComponent, TextureFormat.StencilIndex]:
                if self.depth_attachment_spec:
                    _logger.warning('Multiple depth attachment specifications found. Only the first one will be used.')
                    continue

                self.depth_attachment_spec = attachment_spec
                continue

            self.color_attachment_specs.append(attachment_spec)

    def _create_attachments(self) -> None:
        for attachment_spec in self.color_attachment_specs:
            attachment = self._create_attachment(attachment_spec)
            self.color_attachments.append(attachment)

        if self.depth_attachment_spec:
            self.depth_attachment = self._create_attachment(
                self.depth_attachment_spec)

    def _create_attachment(self, attachment_spec: AttachmentSpec) -> int:
        multisample = self.specification.samples > 1

        target = TextureTarget.Texture2dMultisample if multisample else TextureTarget.Texture2d
        _id = gl.create_texture(target).value

        if multisample:
            GL.glTextureStorage2DMultisample(
                _id, 
                self.specification.samples,
                attachment_spec.texture_format,
                self.width,
                self.height,
                False)
        else:
            GL.glTextureStorage2D(
                _id,
                1,
                attachment_spec.texture_format,
                self.width,
                self.height)

        GL.glTextureParameteri(
            _id,
            TextureParameter.MinFilter,
            attachment_spec.min_filter)
        GL.glTextureParameteri(
            _id,
            TextureParameter.MagFilter,
            attachment_spec.mag_filter)
        GL.glTextureParameteri(
            _id,
            TextureParameter.WrapS,
            attachment_spec.wrap_mode)
        GL.glTextureParameteri(
            _id,
            TextureParameter.WrapT,
            attachment_spec.wrap_mode)
        GL.glTextureParameteri(
            _id,
            TextureParameter.WrapR,
            attachment_spec.wrap_mode)

        return _id

    def _attach_texture(self, _id: int, index: int, attachment_point: AttachmentPoint) -> None:
        attachment = attachment_point
        if attachment == AttachmentPoint.ColorAttachment:
            attachment += index # type: ignore

        GL.glNamedFramebufferTexture(self.id, attachment, _id, 0)

    def _invalidate(self, check_complete: bool) -> None:
        if self.id:
            self._delete()

        self._id = gl.create_framebuffer()

        self._create_attachments()

        if self.depth_attachment_spec:
            self._attach_texture(
                self.depth_attachment, 0,
                self.depth_attachment_spec.attachment_point)

        for idx, attachment_spec in enumerate(self.color_attachment_specs):
            _id = self.color_attachments[idx]
            self._attach_texture(_id, idx, attachment_spec.attachment_point)

        if len(self.color_attachments) > 0:
            # TODO: Extract constant for max color attachments count
            if len(self.color_attachments) > 4:
                raise GraphicsException(
                    'Cannot attach more than 4 color attachments to a single framebuffer.')

            draw_buffers = [
                AttachmentPoint.ColorAttachment + i for i in range(4)]
            GL.glNamedFramebufferDrawBuffers(
                self.id,
                len(self.color_attachments),
                draw_buffers)
        else:
            # TODO: Move GL_NONE to some enum
            GL.glNamedFramebufferDrawBuffer(self.id, GL.GL_NONE)

        if check_complete:
            status = FramebufferStatus(
                GL.glCheckNamedFramebufferStatus(self.id, GL.GL_FRAMEBUFFER))
            if status != FramebufferStatus.Complete:
                raise GraphicsException(
                    f'Framebuffer incomplete: {status.name}')

    def _resize_callback(self, e: events.ResizeEvent) -> None:
        if e.width == 0 or e.height == 0:
            return

        self.resize(e.width, e.height)
