# from ...debugging import Debug, LogLevel
# from ..gl import GLObject

# from OpenGL import GL
# from enum import Enum
# import glm

# _ATTACHMENT_TARGET_MAP = {
# 	GL.GL_DEPTH24_STENCIL8: GL.GL_DEPTH_STENCIL_ATTACHMENT,
# 	GL.GL_RGBA8: GL.GL_COLOR_ATTACHMENT0,
# 	GL.GL_RED_INTEGER: GL.GL_COLOR_ATTACHMENT0,
# 	GL.GL_RGB8: GL.GL_COLOR_ATTACHMENT0
# }

# class FramebufferTextureFormat:
# 	R8 = GL.GL_R8
# 	R8UI = GL.GL_R8UI
# 	Rgba8 = GL.GL_RGBA8
# 	Depth24Stencil8 = GL.GL_DEPTH24_STENCIL8
# 	Depth = Depth24Stencil8

# class FramebufferAttachmentSpec:
# 	def __init__(self, _format: FramebufferTextureFormat):
# 		self._isDepthTexture = False
# 		self._usesRenderBuffer = False
# 		self.textureFormat = _format
# 		self.wrapMode = GL.GL_CLAMP_TO_EDGE
# 		self.minFilter = GL.GL_LINEAR
# 		self.magFilter = GL.GL_LINEAR
# 		self.samples = 1

# class FramebufferSpec:
# 	def __init__(self, width: int, height: int):
# 		self.attachmentsSpecs = []
# 		self.width = width
# 		self.height = height
# 		self.color = glm.vec4(1.0)

# class FramebufferDepthTexture(FramebufferAttachmentSpec):
# 	def __init__(self, useRenderBuffer: bool):
# 		super().__init__(GL.GL_DEPTH24_STENCIL8)

# 		self._isDepthTexture = True
# 		self._usesRenderBuffer = useRenderBuffer
# 		self.minFilter = GL.GL_NEAREST
# 		self.magFilter = GL.GL_NEAREST

# class FramebufferColorTexture(FramebufferAttachmentSpec):
# 	def __init__(self, _format: FramebufferTextureFormat, samples: int = 1):
# 		assert _format != GL.GL_DEPTH24_STENCIL8, "Depth format passed as color texture format."

# 		super().__init__(_format)

# 		self.samples = samples

# class Framebuffer(GLObject):
# 	__PixelFormat = GL.GL_RGBA
# 	__PixelType = GL.GL_UNSIGNED_BYTE

# 	__MaxColorAttachments = 0

# 	def __init__(self, specification: FramebufferSpec):
# 		super().__init__()
# 		if not Framebuffer.__MaxColorAttachments:
# 			Framebuffer.__MaxColorAttachments = GL.glGetInteger(GL.GL_MAX_COLOR_ATTACHMENTS)
			
# 		self.spec = specification

# 		self.__colorAttachments = []
# 		self.__depthAttachment = 0

# 		self.__isDepthAttachmentBuffer = False
# 		self.__lastColorAttachment = 0

# 		self.__Invalidate(False)
	
# 	def __CreateDepthAttachment(self, _format: FramebufferDepthTexture):
# 		multisampled = True if _format.samples > 1 else False

# 		if _format._usesRenderBuffer:
# 			self.__isDepthAttachmentBuffer = True
			
# 			_id = GL.glGenRenderbuffers(1)
# 			GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, _id)

# 			if multisampled:
# 				GL.glRenderbufferStorageMultisample(GL.GL_RENDERBUFFER, _format.samples, _format.textureFormat, self.spec.width, self.spec.height)
# 			else:
# 				GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, _format.textureFormat, self.spec.width, self.spec.height)
			
# 			GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, _ATTACHMENT_TARGET_MAP[_format.textureFormat], GL.GL_RENDERBUFFER, _id)
# 			GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0)
# 		else:
# 			_id = GL.glGenTextures(1)
# 			target = GL.GL_TEXTURE_2D_MULTISAMPLE if _format.samples > 1 else GL.GL_TEXTURE_2D

# 			GL.glBindTexture(target, _id)

# 			GL.glTexParameter(target, GL.GL_TEXTURE_MIN_FILTER, _format.minFilter)
# 			GL.glTexParameter(target, GL.GL_TEXTURE_MAG_FILTER, _format.magFilter)
# 			GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_S, _format.wrapMode)
# 			GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_T, _format.wrapMode)
# 			GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_R, _format.wrapMode)

# 			if multisampled:
# 				GL.glTexStorage2DMultisample(target, 1, _format.textureFormat, self.spec.width, self.spec.height, False)
# 			else:
# 				GL.glTexStorage2D(target, 1, _format.textureFormat, self.spec.width, self.spec.height)
		
# 			GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, _ATTACHMENT_TARGET_MAP[_format.textureFormat], target, _id, 0)
# 			GL.glBindTexture(target, 0)
		
# 		return _id
		
# 	def __CreateColorAttachment(self, _format: FramebufferColorTexture):
# 		multisampled = True if _format.samples > 1 else False
# 		target = GL.GL_TEXTURE_2D_MULTISAMPLE if _format.samples > 1 else GL.GL_TEXTURE_2D

# 		_id = GL.glGenTextures(1)
# 		GL.glBindTexture(target, _id)

# 		GL.glTexParameter(target, GL.GL_TEXTURE_MIN_FILTER, _format.minFilter)
# 		GL.glTexParameter(target, GL.GL_TEXTURE_MAG_FILTER, _format.magFilter)
# 		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_S, _format.wrapMode)
# 		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_T, _format.wrapMode)
# 		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_R, _format.wrapMode)

# 		if multisampled:
# 			GL.glTexImage2DMultisample(target, _format.samples, _format.textureFormat, self.spec.width, self.spec.height, False)
# 		else:
# 			GL.glTexImage2D(target, 0, _format.textureFormat, self.spec.width, self.spec.height, 0, Framebuffer.__PixelFormat, Framebuffer.__PixelType, None)
		
# 		GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, _ATTACHMENT_TARGET_MAP[_format.textureFormat] + self.__lastColorAttachment, target, _id, 0)
# 		GL.glBindTexture(target, 0)

# 		self.__lastColorAttachment += 1

# 		return _id

# 	def __Invalidate(self, resizing: bool) -> None:
# 		if resizing:
# 			self.Delete(True)

# 			self.__colorAttachments.clear()
# 			self.__depthAttachment = 0
# 			self.__lastColorAttachment = 0
		
# 		self._id = GL.glGenFramebuffers(1)
# 		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._id)

# 		for f in self.spec.attachmentsSpecs:
# 			if f._isDepthTexture:
# 				tex = self.__CreateDepthAttachment(f)
# 				self.__depthAttachment = tex
# 			else:
# 				tex = self.__CreateColorAttachment(f)
# 				self.__colorAttachments.append(tex)

# 		if len(self.__colorAttachments) > 1:
# 			assert len(self.__colorAttachments) <= Framebuffer.__MaxColorAttachments, "Too many color attachments"

# 			buffers = [GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1, GL.GL_COLOR_ATTACHMENT2, GL.GL_COLOR_ATTACHMENT3]
# 			GL.glDrawBuffers(len(buffers), buffers)
# 		else:
# 			GL.glDrawBuffer(GL.GL_NONE)

# 		if not resizing:
# 			err = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
# 			if err != GL.GL_FRAMEBUFFER_COMPLETE:
# 				raise RuntimeError(f"Framebuffer (id: {self._id} incomplete: {err}.")
# 			else:
# 				Debug.Log(f"Framebuffer (id: {self._id}) created succesfully", LogLevel.Info)
		
# 		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
	
# 	def Resize(self, width: int, height: int) -> None:
# 		self.spec.width = width
# 		self.spec.height = height

# 		self.__Invalidate(True)

# 	def Bind(self) -> None:
# 		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._id)
# 		GL.glViewport(0, 0, self.spec.width, self.spec.height)
	
# 	def Unbind(self) -> None:
# 		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

# 	def Delete(self, removeRef: bool) -> None:
# 		super().Delete(removeRef)
# 		textures = self.__colorAttachments

# 		if self.__isDepthAttachmentBuffer:
# 			GL.glDeleteRenderbuffers(1, [self.__depthAttachment])
# 		else:
# 			textures.append(self.__depthAttachment)
			
# 		GL.glDeleteTextures(len(textures), textures)
# 		GL.glDeleteFramebuffers(1, [self._id])

# 	def GetColorAttachment(self, idx) -> int:
# 		return self.__colorAttachments[idx]
	
# 	def GetDepthAttachment(self) -> int:
# 		return self.__depthAttachment






from ..gl import GLObject, GLHelper
from ...debugging import Debug, LogLevel
from ...exceptions import GraphicsException
from ...constants import _GL_FB_ERROR_CODE_NAMES_MAP

from OpenGL import GL
from typing import List

_ATTACHMENT_FORMAT_IS_COLOR_MAP = {
	GL.GL_RED_INTEGER: True,
	GL.GL_RGB: True,
	GL.GL_RGBA: True,
	GL.GL_DEPTH24_STENCIL8: False
}

_TEXTURE_FORMAT_INTERNAL_FORMAT_MAP = {
	GL.GL_RED_INTEGER: GL.GL_R32I,
	GL.GL_RGB: GL.GL_RGB8,
	GL.GL_RGBA: GL.GL_RGBA8,
	GL.GL_DEPTH24_STENCIL8: GL.GL_DEPTH24_STENCIL8
}

class FramebufferTextureFormat:
	NoAttachment = 0
	RedInteger = GL.GL_RED_INTEGER
	Rgb = GL.GL_RGB
	Rgba = GL.GL_RGBA
	Depth24Stencil8 = GL.GL_DEPTH24_STENCIL8
	Depth = GL.GL_DEPTH24_STENCIL8

class FramebufferAttachmentSpec(object):
	def __init__(self, _format: FramebufferTextureFormat):
		self.textureFormat = _format
		self.wrapMode = GL.GL_CLAMP_TO_EDGE
		self.minFilter = GL.GL_LINEAR
		self.magFilter = GL.GL_LINEAR

class FramebufferSpec(object):
	def __init__(self, width: int, height: int):
		self.width = width
		self.height = height
		self.samples = 1
		self.attachmentSpecs: List[FramebufferAttachmentSpec] = []

class Framebuffer(GLObject):
	def __init__(self, specification: FramebufferSpec):
		super().__init__()
		self.width = specification.width
		self.height = specification.height
	
		self.colorAttachmentSpecs = []
		self.depthAttachmentSpec = FramebufferAttachmentSpec(FramebufferTextureFormat.NoAttachment)

		self.colorAttachments = []
		self.depthAttachment = 0

		self.specification = specification

		for attachmentSpec in specification.attachmentSpecs:
			if _ATTACHMENT_FORMAT_IS_COLOR_MAP[attachmentSpec.textureFormat]:
				self.colorAttachmentSpecs.append(attachmentSpec)
			else:
				if self.depthAttachmentSpec.textureFormat != FramebufferTextureFormat.NoAttachment:
					Debug.Log("Framebuffer found more than one depth texture format in the specification. Additional depth textures will not be created.", LogLevel.Warning)
					continue
			
				self.depthAttachmentSpec = attachmentSpec
		
		self.__Invalidate(True)

		Debug.GetGLError()
		Debug.Log(f"Framebuffer (id: {self._id}) created succesfully.", LogLevel.Info)
	
	def Bind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self._id)
		GL.glViewport(0, 0, self.width, self.height)
	
	def Unbind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
	
	def Resize(self, width: int, height: int) -> None:
		self.width = width
		self.height = height
		
		self.__Invalidate(False)

		Debug.Log(f"Framebuffer (id: {self._id}) resized to ({width}, {height}).", LogLevel.Info)

	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)

		GL.glDeleteFramebuffers(1, [self._id])
		GL.glDeleteTextures(len(self.colorAttachments), self.colorAttachments)
		GL.glDeleteTextures(1, [self.depthAttachment])

		self.colorAttachments.clear()
		self.depthAttachment = 0
	
	def GetColorAttachment(self, index: int) -> int:
		if index >= len(self.colorAttachments):
			raise GraphicsException(f"Cannot get framebuffer color attachment with index {index}. Max index is {len(self.colorAttachments) - 1}")

		return self.colorAttachments[index]
	
	def GetDepthAttachment(self) -> int:
		if not self.depthAttachment:
			raise GraphicsException("Framebuffer doesn't contain depth attachment.")
		
		return self.depthAttachment
	
	def __CreateFramebufferAttachment(self, attachmentSpec: FramebufferAttachmentSpec) -> int:
		multisample = self.specification.samples > 1
		target = Framebuffer.__GetTextureTarget(multisample)
		internalFormat = _TEXTURE_FORMAT_INTERNAL_FORMAT_MAP[attachmentSpec.textureFormat]

		_id = GLHelper.CreateTexture(target)

		if multisample:
			GL.glTextureStorage2DMultisample(_id, self.specification.samples, internalFormat, self.width, self.height, False)
		else:
			GL.glTextureStorage2D(_id, 1, internalFormat, self.width, self.height)

			GL.glTextureParameteri(_id, GL.GL_TEXTURE_MIN_FILTER, attachmentSpec.minFilter)
			GL.glTextureParameteri(_id, GL.GL_TEXTURE_MAG_FILTER, attachmentSpec.magFilter)
			GL.glTextureParameteri(_id, GL.GL_TEXTURE_WRAP_R, attachmentSpec.wrapMode)
			GL.glTextureParameteri(_id, GL.GL_TEXTURE_WRAP_S, attachmentSpec.wrapMode)
			GL.glTextureParameteri(_id, GL.GL_TEXTURE_WRAP_T, attachmentSpec.wrapMode)

		Debug.GetGLError()

		return _id

	def __AttachFramebufferTexture(self, textureId: int, attachmentIndex: int, isDepthTexture: bool) -> None:
		if isDepthTexture:
			attachmentTarget = GL.GL_DEPTH_STENCIL_ATTACHMENT
		else:
			attachmentTarget = GL.GL_COLOR_ATTACHMENT0 + attachmentIndex
		
		GL.glNamedFramebufferTexture(self._id, attachmentTarget, textureId, 0)

	def __Invalidate(self, checkComplete: bool):
		if self._id:
			self.Delete(False)

		self._id = GLHelper.CreateFramebuffer()

		for idx, attachmentSpec in enumerate(self.colorAttachmentSpecs):
			texture = self.__CreateFramebufferAttachment(attachmentSpec)
			self.__AttachFramebufferTexture(texture, idx, False)
			self.colorAttachments.append(texture)
		 
		if self.depthAttachmentSpec.textureFormat != FramebufferTextureFormat.NoAttachment:
			texture = self.__CreateFramebufferAttachment(self.depthAttachmentSpec)
			self.__AttachFramebufferTexture(texture, 0, True)
			self.depthAttachment = texture
		
		if len(self.colorAttachments) > 1:
			if len(self.colorAttachments) > 4:
				raise GraphicsException("Cannot use more than 4 framebuffer texture attachments.")
			
			drawBuffers = [GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1, GL.GL_COLOR_ATTACHMENT2, GL.GL_COLOR_ATTACHMENT3]
			GL.glNamedFramebufferDrawBuffers(self._id, len(self.colorAttachments), drawBuffers)
		elif len(self.colorAttachments) == 0:
			GL.glNamedFramebufferDrawBuffer(self._id, GL.GL_NONE)
		
		if checkComplete:
			status = GL.glCheckNamedFramebufferStatus(self._id, GL.GL_FRAMEBUFFER)
			if status != GL.GL_FRAMEBUFFER_COMPLETE:
				raise GraphicsException(f"Framebuffer incomplete: {_GL_FB_ERROR_CODE_NAMES_MAP[status]}.")
	
	@staticmethod
	def __GetTextureTarget(isMultisampled: bool) -> GL.GLenum:
		return GL.GL_TEXTURE_2D_MULTISAMPLE if isMultisampled else GL.GL_TEXTURE_2D