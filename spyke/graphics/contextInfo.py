from .capabilities import Capabilities
from ..enums import NvidiaIntegerName, Vendor
from ..utils import EnsureString
from ..autoslot import Slots
from ..exceptions import GraphicsException

from OpenGL import GL

class ContextInfo(Slots):
	__slots__ = ("__weakref__", )
	
	def __init__(self):
		self.renderer = ""
		self.version = ""
		self.glslVersion = ""
		self.vendor = Vendor.Unknown
		self.memoryAvailable = 0
		self.extensions = []
		self.capabilities = Capabilities()

	def GetInfo(self):
		self.renderer = EnsureString(GL.glGetString(GL.GL_RENDERER))
		self.version = EnsureString(GL.glGetString(GL.GL_VERSION))
		self.glslVersion = EnsureString(GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION))
		
		vendor = EnsureString(GL.glGetString(GL.GL_VENDOR)).lower()
		if "nvidia" in vendor:
			self.vendor = Vendor.Nvidia
		elif "intel" in vendor:
			self.vendor = Vendor.Intel
		elif "ati" in vendor:
			self.vendor = Vendor.Amd
		elif "microsoft" in vendor:
			self.vendor = Vendor.WindowsSoftware

		if self.vendor == Vendor.Nvidia:
			self.memoryAvailable = GL.glGetIntegerv(NvidiaIntegerName.GpuMemInfoTotalAvailable)
		
		extCount = GL.glGetInteger(GL.GL_NUM_EXTENSIONS)
		for i in range(extCount):
			self.extensions.append(EnsureString(GL.glGetStringi(GL.GL_EXTENSIONS, i)))

		if not "GL_EXT_direct_state_access" in self.extensions and \
			not "GL_ARB_uniform_buffer_object" in self.extensions and \
			not "GL_ARB_texture_buffer_object" in self.extensions:
			raise GraphicsException("This graphics device doesn't meet the engine requirements.")
		
		if "GL_ARB_texture_compression" in self.extensions:
			self.capabilities.arbTextureCompressionEnabled = True
		
		if "GL_ARB_bindless_texture" in self.extensions:
			self.capabilities.arbBindlessTextureEnabled = True
		
		if "GL_NV_command_list" in self.extensions:
			self.capabilities.nvCommandListEnabled = True
		
		if "GL_INTEL_framebuffer_CMAA" in self.extensions:
			self.capabilities.intelFramebufferCMAAEnabled = True