from ..enums import NvidiaIntegerName, Vendor
from ..utils import EnsureString
from ..autoslot import WeakSlots

from OpenGL import GL

class ContextInfo(WeakSlots):
	def __init__(self):
		self.renderer = ""
		self.version = ""
		self.glslVersion = ""
		self.vendor = Vendor.Unknown
		self.memoryAvailable = 0

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