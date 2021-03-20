from ...debugging import Debug, LogLevel
from ...memory import GLMarshal

from OpenGL import GL
import glm

_ATTACHMENT_TARGET_MAP = {
	GL.GL_DEPTH24_STENCIL8: GL.GL_DEPTH_STENCIL_ATTACHMENT,
	GL.GL_RGBA8: GL.GL_COLOR_ATTACHMENT0,
	GL.GL_RED_INTEGER: GL.GL_COLOR_ATTACHMENT0,
	GL.GL_RGB8: GL.GL_COLOR_ATTACHMENT0
}

class FramebufferTextureFormat:
	Rgba8 = GL.GL_RGBA8
	Depth24Stencil8 = GL.GL_DEPTH24_STENCIL8
	Depth = Depth24Stencil8

class FramebufferAttachmentSpec:
	def __init__(self, _format: FramebufferTextureFormat):
		self._isDepthTexture = False
		self._usesRenderBuffer = False
		self.textureFormat = _format
		self.wrapMode = GL.GL_CLAMP_TO_EDGE
		self.minFilter = GL.GL_LINEAR
		self.magFilter = GL.GL_LINEAR
		self.samples = 1

class FramebufferSpec:
	def __init__(self, width: int, height: int):
		self.attachmentsSpecs = []
		self.width = width
		self.height = height
		self.color = glm.vec4(1.0)

class FramebufferDepthTexture(FramebufferAttachmentSpec):
	def __init__(self, useRenderBuffer: bool):
		super().__init__(GL.GL_DEPTH24_STENCIL8)

		self._isDepthTexture = True
		self._usesRenderBuffer = useRenderBuffer
		self.minFilter = GL.GL_NEAREST
		self.magFilter = GL.GL_NEAREST

class FramebufferColorTexture(FramebufferAttachmentSpec):
	def __init__(self, _format: FramebufferTextureFormat, samples: int = 1):
		assert _format != GL.GL_DEPTH24_STENCIL8, "Depth format passed as color texture format."

		super().__init__(_format)

		self.samples = samples

class Framebuffer(object):
	__PixelFormat = GL.GL_RGBA
	__PixelType = GL.GL_UNSIGNED_BYTE

	__MaxColorAttachments = 0

	def __init__(self, specification: FramebufferSpec):
		if not Framebuffer.__MaxColorAttachments:
			Framebuffer.__MaxColorAttachments = GL.glGetInteger(GL.GL_MAX_COLOR_ATTACHMENTS)
			
		self.spec = specification

		self.__colorAttachments = []
		self.__depthAttachment = 0

		self.__isDepthAttachmentBuffer = False
		self.__lastColorAttachment = 0

		self.__Invalidate(False)

		GLMarshal.AddObjectRef(self)
	
	def __CreateDepthAttachment(self, _format: FramebufferDepthTexture):
		multisampled = True if _format.samples > 1 else False

		if _format._usesRenderBuffer:
			self.__isDepthAttachmentBuffer = True
			
			_id = GL.glGenRenderbuffers(1)
			GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, _id)

			if multisampled:
				GL.glRenderbufferStorageMultisample(GL.GL_RENDERBUFFER, _format.samples, _format.textureFormat, self.spec.width, self.spec.height)
			else:
				GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, _format.textureFormat, self.spec.width, self.spec.height)
			
			GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, _ATTACHMENT_TARGET_MAP[_format.textureFormat], GL.GL_RENDERBUFFER, _id)
			GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0)
		else:
			_id = GL.glGenTextures(1)
			target = GL.GL_TEXTURE_2D_MULTISAMPLE if _format.samples > 1 else GL.GL_TEXTURE_2D

			GL.glBindTexture(target, _id)

			GL.glTexParameter(target, GL.GL_TEXTURE_MIN_FILTER, _format.minFilter)
			GL.glTexParameter(target, GL.GL_TEXTURE_MAG_FILTER, _format.magFilter)
			GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_S, _format.wrapMode)
			GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_T, _format.wrapMode)
			GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_R, _format.wrapMode)

			if multisampled:
				GL.glTexStorage2DMultisample(target, 1, _format.textureFormat, self.spec.width, self.spec.height, False)
			else:
				GL.glTexStorage2D(target, 1, _format.textureFormat, self.spec.width, self.spec.height)
		
			GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, _ATTACHMENT_TARGET_MAP[_format.textureFormat], target, _id, 0)
			GL.glBindTexture(target, 0)
		
		return _id
		
	def __CreateColorAttachment(self, _format: FramebufferColorTexture):
		multisampled = True if _format.samples > 1 else False
		target = GL.GL_TEXTURE_2D_MULTISAMPLE if _format.samples > 1 else GL.GL_TEXTURE_2D

		_id = GL.glGenTextures(1)
		GL.glBindTexture(target, _id)

		GL.glTexParameter(target, GL.GL_TEXTURE_MIN_FILTER, _format.minFilter)
		GL.glTexParameter(target, GL.GL_TEXTURE_MAG_FILTER, _format.magFilter)
		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_S, _format.wrapMode)
		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_T, _format.wrapMode)
		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_R, _format.wrapMode)

		if multisampled:
			GL.glTexImage2DMultisample(target, _format.samples, _format.textureFormat, self.spec.width, self.spec.height, False)
		else:
			GL.glTexImage2D(target, 0, _format.textureFormat, self.spec.width, self.spec.height, 0, Framebuffer.__PixelFormat, Framebuffer.__PixelType, None)
		
		GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, _ATTACHMENT_TARGET_MAP[_format.textureFormat] + self.__lastColorAttachment, target, _id, 0)
		GL.glBindTexture(target, 0)

		self.__lastColorAttachment += 1

		return _id

	def __Invalidate(self, resizing: bool) -> None:
		if resizing:
			self.Delete(True)

			self.__colorAttachments.clear()
			self.__depthAttachment = 0
			self.__lastColorAttachment = 0
		
		self.__id = GL.glGenFramebuffers(1)
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.__id)

		for f in self.spec.attachmentsSpecs:
			if f._isDepthTexture:
				tex = self.__CreateDepthAttachment(f)
				self.__depthAttachment = tex
			else:
				tex = self.__CreateColorAttachment(f)
				self.__colorAttachments.append(tex)

		if len(self.__colorAttachments) > 1:
			assert len(self.__colorAttachments) <= Framebuffer.__MaxColorAttachments, "Too many color attachments"

			buffers = [GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1, GL.GL_COLOR_ATTACHMENT2, GL.GL_COLOR_ATTACHMENT3]
			GL.glDrawBuffers(len(buffers), buffers)
		else:
			GL.glDrawBuffer(GL.GL_NONE)

		if not resizing:
			err = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
			if err != GL.GL_FRAMEBUFFER_COMPLETE:
				raise RuntimeError(f"Framebuffer (id: {self.__id} incomplete: {err}.")
			else:
				Debug.Log(f"Framebuffer (id: {self.__id}) created succesfully", LogLevel.Info)
		
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
	
	def Resize(self, width: int, height: int) -> None:
		self.spec.width = width
		self.spec.height = height

		self.__Invalidate(True)

	def Bind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.__id)
		GL.glViewport(0, 0, self.spec.width, self.spec.height)
	
	def Unbind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

	def Delete(self, removeRef: bool) -> None:
		textures = self.__colorAttachments

		if self.__isDepthAttachmentBuffer:
			GL.glDeleteRenderbuffers(1, [self.__depthAttachment])
		else:
			textures.append(self.__depthAttachment)
			
		GL.glDeleteTextures(len(textures), textures)
		GL.glDeleteFramebuffers(1, [self.__id])

		if removeRef:
			GLMarshal.RemoveObjectRef(self)
	
	def GetColorAttachment(self, idx) -> int:
		return self.__colorAttachments[idx]
	
	def GetDepthAttachment(self) -> int:
		return self.__depthAttachment
	
	@staticmethod
	def UnbindAll() -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
	
	@property
	def ID(self) -> int:
		return self.__id