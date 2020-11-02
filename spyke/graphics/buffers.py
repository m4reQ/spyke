from .. import USE_FAST_MIN_FILTER
from ..utils import INT_SIZE, GetPointer, ObjectManager
from ..enums import BufferUsageFlag

from OpenGL import GL
import numpy

class DynamicVertexBuffer(object):
	def __init__(self, size: int, usage = BufferUsageFlag.StreamDraw):
		self.__size = size
		self.__id = GL.glGenBuffers(1)

		self.__usageFlag = usage
		
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.__id)
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.__size, None, self.__usageFlag)
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

		ObjectManager.AddObject(self)

	def AddData(self, data: list, size: int) -> None:
		GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, size, numpy.asarray(data, dtype=numpy.float32))
	
	def Bind(self) -> None:
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.__id)
	
	def Unbind(self) -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
	
	def Delete(self) -> None:
		GL.glDeleteBuffers(1, [self.__id])
	
	def Clear(self) -> None:
		GL.glBufferData(GL.GL_ARRAY_BUFFER, self.__size, None, self.__usageFlag)
	
	@property
	def Size(self):
		return self.__size
	
	@property
	def ID(self):
		return self.__id
	
	@staticmethod
	def UnbindAll() -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

class StaticIndexBuffer(object):
	def __init__(self, data: list):
		self.__size = len(data) * INT_SIZE
		self.__id = GL.glGenBuffers(1)
		
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.__id)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.__size, numpy.asarray(data, dtype=numpy.int32), GL.GL_STATIC_DRAW)
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

		ObjectManager.AddObject(self)
	
	def Bind(self) -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.__id)
	
	def Unbind(self) -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
	
	def Delete(self) -> None:
		GL.glDeleteBuffers(1, [self.__id])
	
	@property
	def Size(self):
		return self.__size
	
	@property
	def ID(self):
		return self.__id
	
	@staticmethod
	def UnbindAll() -> None:
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

class FramebufferSpecs(object):
	def __init__(self, width: int, height: int):
		self.Width = width
		self.Height = height
		self.Samples = 1
		self.HasDepthAttachment = False

class Framebuffer(object):
	__InternalFormat = GL.GL_RGBA8
	__PixelFormat = GL.GL_RGBA
	__PixelType = GL.GL_UNSIGNED_BYTE

	if USE_FAST_MIN_FILTER:
		__MinFilter = GL.GL_LINEAR
	else:
		__MinFilter = GL.GL_NEAREST

	def __init__(self, specification: FramebufferSpecs):
		self.__spec = specification

		self.__Invalidate(False)

		ObjectManager.AddObject(self)

	def __Invalidate(self, resizing: bool) -> None:
		if resizing:
			self.Delete()
		
		self.__colorAttachmentId = GL.glGenTextures(1)
		self.__depthAttachmentId = -1

		if self.__spec.Samples > 1:
			GL.glBindTexture(GL.GL_TEXTURE_2D_MULTISAMPLE, self.__colorAttachmentId)
			GL.glTexImage2DMultisample(GL.GL_TEXTURE_2D_MULTISAMPLE, self.__spec.Samples, Framebuffer.__InternalFormat, self.__spec.Width, self.__spec.Height, False)
		else:
			GL.glBindTexture(GL.GL_TEXTURE_2D, self.__colorAttachmentId)
			GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, Framebuffer.__InternalFormat, self.__spec.Width, self.__spec.Height, 0, Framebuffer.__PixelFormat, Framebuffer.__PixelType, None) ################################
			GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MIN_FILTER, Framebuffer.__MinFilter)
			GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
		
		self.__id = GL.glGenFramebuffers(1)
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.__id)
		GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D_MULTISAMPLE if self.__spec.Samples > 4 else GL.GL_TEXTURE_2D, self.__colorAttachmentId, 0)

		if self.__spec.HasDepthAttachment:
			GL.glBindTexture(GL.GL_TEXTURE_2D, self.__depthAttachmentId)
			GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT, self.__spec.Width, self.__spec.Height, 0, GL.GL_DEPTH_COMPONENT, Framebuffer.__PixelType, None)
			GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, self.__depthAttachmentId, 0)

			GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MIN_FILTER, Framebuffer.__MinFilter)
			GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
			GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
			GL.glTexParameter(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

		GL.glDrawBuffer(GL.GL_NONE)
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
		
		if not resizing:
			err = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
			if err != GL.GL_FRAMEBUFFER_COMPLETE:
				raise RuntimeError(f"Framebuffer {self.__id} incomplete: {err}.")
	
	def Resize(self, width: int, height: int) -> None:
		self.__spec.Width = width
		self.__spec.Height = height

		self.__Invalidate(True)

	def Bind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.__id)
	
	def Unbind(self) -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)

	def Delete(self) -> None:
		GL.glDeleteTextures([self.__colorAttachmentId])
		GL.glDeleteFramebuffers(1, [self.__id])
	
	@staticmethod
	def UnbindAll() -> None:
		GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)