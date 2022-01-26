from __future__ import annotations
import typing

from spyke.graphics.texturing.textureProxy import TextureProxy
if typing.TYPE_CHECKING:
    from typing import List

from spyke.enums import AttachmentPoint, FramebufferStatus, MagFilter, MinFilter, SizedInternalFormat, TextureFormat, TextureParameter, TextureTarget, WrapMode
from spyke.graphics import gl
from spyke.exceptions import GraphicsException
from spyke import debug
from spyke import events

from OpenGL import GL


class AttachmentSpec:
    __slots__ = (
        'min_filter',
        'mag_filter',
        'wrap_mode',
        'texture_format'
    )

    def __init__(self, texture_format: SizedInternalFormat):
        self.min_filter: MinFilter = MinFilter.LinearMipmapLinear
        self.mag_filter: MagFilter = MagFilter.Linear
        self.wrap_mode: WrapMode = WrapMode.Repeat
        self.texture_format: SizedInternalFormat = texture_format

    @property
    def attachment_point(self) -> AttachmentPoint:
        if self.texture_format in [SizedInternalFormat.DepthComponent16, SizedInternalFormat.DepthComponent24, SizedInternalFormat.DepthComponent32f]:
            return AttachmentPoint.DepthAttachment
        if self.texture_format in [SizedInternalFormat.Depth24Stencil8, SizedInternalFormat.Depth32fStencil8]:
            return AttachmentPoint.DepthStencilAttachment
        if self.texture_format == SizedInternalFormat.StencilIndex8:
            return AttachmentPoint.StencilAttachment
        else:
            return AttachmentPoint.ColorAttachment


class FramebufferSpec:
    __slots__ = (
        '__weakref__',
        'width',
        'height',
        'samples',
        'is_resizable',
        'attachments_specs'
    )

    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.samples: int = 1
        self.is_resizable: bool = False
        self.attachments_specs: List[AttachmentSpec] = []

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

        self.color_attachment_specs: List[AttachmentSpec] = []
        self.depth_attachment_spec: AttachmentSpec = None

        self._get_attachments_specs(specification)

        self.color_attachments: List[int] = []
        self.depth_attachment: int = 0

        self._invalidate(True)

        if specification.is_resizable:
            events.register_method(self._resize_callback,
                                   events.ResizeEvent, priority=-2)

        debug.get_gl_error()
        debug.log_info(f'{self} created succesfully.')

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

        debug.log_info(f'{self} resized to ({width}, {height}).')

    def delete(self) -> None:
        GL.glDeleteFramebuffers(1, [self.id])
        GL.glDeleteTextures(len(self.color_attachments) + 1,
                            self.color_attachments + [self.depth_attachment, ])

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
                    debug.log_warning(
                        'Multiple depth attachment specifications found. Only the first one will be used.')
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
                _id, self.specification.samples, attachment_spec.texture_format, self.width, self.height, False)
        else:
            GL.glTextureStorage2D(
                _id, 1, attachment_spec.texture_format, self.width, self.height)

        GL.glTextureParameteri(
            _id, TextureParameter.TextureMinFilter, attachment_spec.min_filter)
        GL.glTextureParameteri(
            _id, TextureParameter.TextureMagFilter, attachment_spec.mag_filter)
        GL.glTextureParameteri(
            _id, TextureParameter.TextureWrapS, attachment_spec.wrap_mode)
        GL.glTextureParameteri(
            _id, TextureParameter.TextureWrapT, attachment_spec.wrap_mode)
        GL.glTextureParameteri(
            _id, TextureParameter.TextureWrapR, attachment_spec.wrap_mode)

        return _id

    def _attach_texture(self, _id: int, index: int, attachment_point: AttachmentPoint) -> None:
        attachment = attachment_point
        if attachment == AttachmentPoint.ColorAttachment:
            attachment += index

        GL.glNamedFramebufferTexture(self.id, attachment, _id, 0)

    def _invalidate(self, check_complete: bool) -> None:
        if self.id:
            self.delete()

        self._id = gl.create_framebuffer()

        self._create_attachments()

        if self.depth_attachment:
            self._attach_texture(self.depth_attachment, 0,
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
                self.id, len(self.color_attachments), draw_buffers)
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
