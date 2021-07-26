from ..gl import GLObject, GLHelper
from ...debugging import Debug, LogLevel
from ...exceptions import GraphicsException
from ...constants import _GL_FB_ERROR_CODE_NAMES_MAP, _NP_FLOAT, _NP_INT
from ...autoslot import Slots

from OpenGL import GL
from typing import List, Tuple
import numpy as np

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

class FramebufferAttachmentSpec(Slots):
	__slots__ = ("__weakref__", )

	def __init__(self, _format: FramebufferTextureFormat):
		self.textureFormat = _format
		self.wrapMode = GL.GL_CLAMP_TO_EDGE
		self.minFilter = GL.GL_LINEAR
		self.magFilter = GL.GL_LINEAR

class FramebufferSpec(Slots):
	__slots__ = ("__weakref__", )
	
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
				if self.depthAttachmentSpec.textureFormat:
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
	
	def ClearBufferInt(self, bufferTraget: GL.GLenum, drawBuffer: int, value: Tuple[int, int, int, int]) -> None:
		GL.glClearNamedFramebufferiv(self._id, bufferTraget, drawBuffer, np.asarray(value, dtype=_NP_INT))

	def ClearBufferFloat(self, bufferTraget: GL.GLenum, drawBuffer: int, value: Tuple[float, float, float, float]) -> None:
		GL.glClearNamedFramebufferfv(self._id, bufferTraget, drawBuffer, np.asarray(value, dtype=_NP_FLOAT))
	
	def __CreateFramebufferAttachment(self, attachmentSpec: FramebufferAttachmentSpec) -> int:
		multisample = self.specification.samples > 1
		target = GL.GL_TEXTURE_2D_MULTISAMPLE if multisample else GL.GL_TEXTURE_2D
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
		 
		if self.depthAttachmentSpec.textureFormat:
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
		else: #means we have only one color attachment
			GL.glNamedFramebufferDrawBuffer(self._id, GL.GL_COLOR_ATTACHMENT0) #assume we use 0th index for our attachment
		
		if checkComplete:
			status = GL.glCheckNamedFramebufferStatus(self._id, GL.GL_FRAMEBUFFER)
			if status != GL.GL_FRAMEBUFFER_COMPLETE:
				raise GraphicsException(f"Framebuffer incomplete: {_GL_FB_ERROR_CODE_NAMES_MAP[status]}.")