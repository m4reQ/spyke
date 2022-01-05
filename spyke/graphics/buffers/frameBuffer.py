from spyke.graphics import gl
from spyke.exceptions import GraphicsException
from spyke import debug
from ...constants import _GL_FB_ERROR_CODE_NAMES_MAP, _NP_FLOAT, _NP_INT

from OpenGL import GL
from typing import List, Tuple
import numpy as np

_ATTACHMENT_FORMAT_IS_COLOR_MAP = {
    GL.GL_RED_INTEGER: True,
    GL.GL_RGB: True,
    GL.GL_RGBA: True,
    GL.GL_DEPTH24_STENCIL8: False
}

# TODO: Add support for 16 and 32 bits rgb(a) formats
_TEXTURE_FORMAT_INTERNAL_FORMAT_MAP = {
    GL.GL_RED_INTEGER: GL.GL_R32I,
    GL.GL_RED: GL.GL_R32F,
    GL.GL_RGB: GL.GL_RGB8,
    GL.GL_RGBA: GL.GL_RGBA8,
    GL.GL_DEPTH24_STENCIL8: GL.GL_DEPTH24_STENCIL8
}


class FramebufferAttachmentSpec:
    __slots__ = (
        '__weakref__',
        'textureFormat',
        'wrapMode',
        'minFilter',
        'magFilter'
    )

    # TODO: Change _format type hint to use specific enum (IntenalFormat or something)
    def __init__(self, _format: GL.GLenum):
        self.textureFormat: GL.GLenum = _format
        self.wrapMode: GL.GLenum = GL.GL_CLAMP_TO_EDGE
        self.minFilter: GL.GLenum = GL.GL_LINEAR
        self.magFilter: GL.GLenum = GL.GL_LINEAR


class FramebufferSpec:
    __slots__ = (
        '__weakref__',
        'width',
        'height',
        'samples',
        'attachment_specs'
    )

    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.samples: int = 1
        self.attachment_specs: List[FramebufferAttachmentSpec] = []


class Framebuffer(gl.GLObject):
    def __init__(self, specification: FramebufferSpec):
        super().__init__()

        self._id = gl.create_framebuffer()

        self.width = specification.width
        self.height = specification.height

        self.colorAttachmentSpecs = []
        self.depthAttachmentSpec = FramebufferAttachmentSpec(0)

        self.colorAttachments = []
        self.depthAttachment = 0

        self.specification = specification

        for attachmentSpec in specification.attachment_specs:
            if _ATTACHMENT_FORMAT_IS_COLOR_MAP[attachmentSpec.textureFormat]:
                self.colorAttachmentSpecs.append(attachmentSpec)
            else:
                if self.depthAttachmentSpec.textureFormat:
                    debug.log_warning(
                        f'{self} found more than one depth texture format in the specification. Additional depth textures will not be created.')
                    continue

                self.depthAttachmentSpec = attachmentSpec

        self.__Invalidate(True)

        debug.get_gl_error()
        debug.log_info(f'{self} created succesfully.')

    def bind(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.id)
        GL.glViewport(0, 0, self.width, self.height)

    def Unbind(self) -> None:
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

    def Resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.__Invalidate(False)

        debug.log_info(f'{self} resized to ({width}, {height}).')

    def delete(self) -> None:
        GL.glDeleteFramebuffers(1, [self.id])
        GL.glDeleteTextures(len(self.colorAttachments), self.colorAttachments)
        GL.glDeleteTextures(1, [self.depthAttachment])

        self.colorAttachments.clear()
        self.depthAttachment = 0

    def GetColorAttachment(self, index: int) -> int:
        if index >= len(self.colorAttachments):
            raise GraphicsException(
                f"Cannot get framebuffer color attachment with index {index}. Max index is {len(self.colorAttachments) - 1}")

        return self.colorAttachments[index]

    def GetDepthAttachment(self) -> int:
        if not self.depthAttachment:
            raise GraphicsException(
                "Framebuffer doesn't contain depth attachment.")

        return self.depthAttachment

    def ClearBufferInt(self, bufferTraget: GL.GLenum, drawBuffer: int, value) -> None:
        GL.glClearNamedFramebufferiv(
            self.id, bufferTraget, drawBuffer, np.asarray(value, dtype=_NP_INT))

    def ClearBufferFloat(self, bufferTraget: GL.GLenum, drawBuffer: int, value) -> None:
        GL.glClearNamedFramebufferfv(
            self.id, bufferTraget, drawBuffer, np.asarray(value, dtype=_NP_FLOAT))

    def __CreateFramebufferAttachment(self, attachmentSpec: FramebufferAttachmentSpec) -> int:
        multisample = self.specification.samples > 1
        target = GL.GL_TEXTURE_2D_MULTISAMPLE if multisample else GL.GL_TEXTURE_2D
        internalFormat = _TEXTURE_FORMAT_INTERNAL_FORMAT_MAP[attachmentSpec.textureFormat]

        _id = gl.create_texture(target).value

        if multisample:
            GL.glTextureStorage2DMultisample(
                _id, self.specification.samples, internalFormat, self.width, self.height, False)
        else:
            GL.glTextureStorage2D(_id, 1, internalFormat,
                                  self.width, self.height)

            GL.glTextureParameteri(
                _id, GL.GL_TEXTURE_MIN_FILTER, attachmentSpec.minFilter)
            GL.glTextureParameteri(
                _id, GL.GL_TEXTURE_MAG_FILTER, attachmentSpec.magFilter)
            GL.glTextureParameteri(
                _id, GL.GL_TEXTURE_WRAP_R, attachmentSpec.wrapMode)
            GL.glTextureParameteri(
                _id, GL.GL_TEXTURE_WRAP_S, attachmentSpec.wrapMode)
            GL.glTextureParameteri(
                _id, GL.GL_TEXTURE_WRAP_T, attachmentSpec.wrapMode)

        debug.get_gl_error()

        return _id

    def __AttachFramebufferTexture(self, textureId: int, attachmentIndex: int, isDepthTexture: bool) -> None:
        if isDepthTexture:
            attachmentTarget = GL.GL_DEPTH_STENCIL_ATTACHMENT
        else:
            attachmentTarget = GL.GL_COLOR_ATTACHMENT0 + attachmentIndex

        GL.glNamedFramebufferTexture(self.id, attachmentTarget, textureId, 0)

    def __Invalidate(self, checkComplete: bool):
        if self.id:
            self.delete()

        self._id = gl.create_framebuffer()

        for idx, attachmentSpec in enumerate(self.colorAttachmentSpecs):
            texture = self.__CreateFramebufferAttachment(attachmentSpec)
            self.__AttachFramebufferTexture(texture, idx, False)
            self.colorAttachments.append(texture)

        if self.depthAttachmentSpec.textureFormat:
            texture = self.__CreateFramebufferAttachment(
                self.depthAttachmentSpec)
            self.__AttachFramebufferTexture(texture, 0, True)
            self.depthAttachment = texture

        if len(self.colorAttachments) > 1:
            if len(self.colorAttachments) > 4:
                raise GraphicsException(
                    "Cannot use more than 4 framebuffer texture attachments.")

            drawBuffers = [GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1,
                           GL.GL_COLOR_ATTACHMENT2, GL.GL_COLOR_ATTACHMENT3]
            GL.glNamedFramebufferDrawBuffers(
                self.id, len(self.colorAttachments), drawBuffers)
        elif len(self.colorAttachments) == 0:
            GL.glNamedFramebufferDrawBuffer(self.id, GL.GL_NONE)
        else:  # means we have only one color attachment
            # assume we use 0th index for our attachment
            GL.glNamedFramebufferDrawBuffer(self.id, GL.GL_COLOR_ATTACHMENT0)

        if checkComplete:
            status = GL.glCheckNamedFramebufferStatus(
                self.id, GL.GL_FRAMEBUFFER)
            if status != GL.GL_FRAMEBUFFER_COMPLETE:
                raise GraphicsException(
                    f"Framebuffer incomplete: {_GL_FB_ERROR_CODE_NAMES_MAP[status]}.")
