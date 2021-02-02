from ...debugging import Log, LogLevel
from ...managers.objectManager import ObjectManager

from OpenGL import GL
import glm

class FramebufferTextureFormat:
	Rgba8 = GL.GL_RGBA8
	Depth24Stencil8 = GL.GL_DEPTH24_STENCIL8
	Depth = Depth24Stencil8

class FramebufferAttachmentSpec:
	def __init__(self, _format: FramebufferTextureFormat):
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

class Framebuffer(object):
	__PixelFormat = GL.GL_RGBA
	__PixelType = GL.GL_UNSIGNED_BYTE

	def __init__(self, specification: FramebufferSpec):
		self.spec = specification

		self.__colorAttachments = []
		self.__depthAttachment = 0

		self.__Invalidate(False)

		ObjectManager.AddObject(self)
	
	def __CreateFramebufferTexture(self, _format: FramebufferAttachmentSpec, idx: int) -> int:
		tex = GL.glGenTextures(1)
		target = GL.GL_TEXTURE_2D if _format.samples == 1 else GL.GL_TEXTURE_2D_MULTISAMPLE

		GL.glBindTexture(target, tex)

		GL.glTexParameter(target, GL.GL_TEXTURE_MIN_FILTER, _format.minFilter)
		GL.glTexParameter(target, GL.GL_TEXTURE_MAG_FILTER, _format.magFilter)
		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_S, _format.wrapMode)
		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_T, _format.wrapMode)
		GL.glTexParameter(target, GL.GL_TEXTURE_WRAP_R, _format.wrapMode)

		if _format.textureFormat == FramebufferTextureFormat.Depth:
			if target == GL.GL_TEXTURE_2D:
				GL.glTexStorage2D(target, 1, _format.textureFormat, self.spec.width, self.spec.height)
			else:
				GL.glTexStorage2DMultisample(target, 1, _format.textureFormat, self.spec.width, self.spec.height)
			
			GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, _format.textureFormat, target, tex, 0)
		else:
			if target == GL.GL_TEXTURE_2D:
				GL.glTexImage2D(target, 0, _format.textureFormat, self.spec.width, self.spec.height, 0, Framebuffer.__PixelFormat, Framebuffer.__PixelType, None)
			else:
				GL.glTexImage2DMultisample(target, _format.samples, _format.textureFormat, self.spec.width, self.spec.height, False)
			
			GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0 + idx, target, tex, 0)

		GL.glBindTexture(target, 0)
		return tex

	def __Invalidate(self, resizing: bool) -> None:
		if resizing:
			self.Delete()

			self.__colorAttachments.clear()
			self.__depthAttachment = 0
		
		self.__id = GL.glGenFramebuffers(1)
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.__id)

		for idx, f in enumerate(self.spec.attachmentsSpecs):
			if f.textureFormat == FramebufferTextureFormat.Depth:
				self.__depthAttachment = self.__CreateFramebufferTexture(f, 0)
			else:
				tex = self.__CreateFramebufferTexture(f, idx)
				self.__colorAttachments.append(tex)
		
		if len(self.__colorAttachments) > 1:
			assert(len(self.__colorAttachments) <= 4)

			buffers = [GL.GL_COLOR_ATTACHMENT0, GL.GL_COLOR_ATTACHMENT1, GL.GL_COLOR_ATTACHMENT2, GL.GL_COLOR_ATTACHMENT3]
			GL.glDrawBuffers(len(self.__colorAttachments), buffers)
		elif len(self.__colorAttachments) == 0:
			GL.glDrawBuffer(GL.GL_NONE)
		
		if not resizing:
			err = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
			if err != GL.GL_FRAMEBUFFER_COMPLETE:
				raise RuntimeError(f"Framebuffer (id: {self.__id} incomplete: {err}.")
			else:
				Log(f"Framebuffer (id: {self.__id}) created succesfully", LogLevel.Info)
		
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
	
	def Resize(self, width: int, height: int) -> None:
		self.spec.width = width
		self.spec.height = height

		self.__Invalidate(True)

	def Bind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.__id)
	
	def Unbind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

	def Delete(self) -> None:
		textures = self.__colorAttachments
		if self.__depthAttachment != -1:
			textures.append(self.__depthAttachment)
		
		GL.glDeleteTextures(len(textures), textures)
		GL.glDeleteFramebuffers(1, [self.__id])
	
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