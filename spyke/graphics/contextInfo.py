#region Import
from ..enums import NvidiaIntegerName, Vendor
from ..utils import EnsureString

from OpenGL import GL
#endregion

class ContextInfo:
	Renderer = ""
	Vendor = Vendor.Unknown
	Version = ""
	GLSLVersion = ""
	MemoryAvailable = 0

	__Checked = False

	@staticmethod
	def TryGetInfo():
		ContextInfo.Renderer = EnsureString(GL.glGetString(GL.GL_RENDERER))
		ContextInfo.Version = EnsureString(GL.glGetString(GL.GL_VERSION))
		ContextInfo.GLSLVersion = EnsureString(GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION))

		vendor = EnsureString(GL.glGetString(GL.GL_VENDOR)).lower()
		if "nvidia" in vendor:
			ContextInfo.Vendor = Vendor.Nvidia
		elif "intel" in vendor:
			ContextInfo.Vendor = Vendor.Intel
		elif "amd" in vendor:
			ContextInfo.Vendor = Vendor.Amd
		else:
			ContextInfo.Vendor = Vendor.Unknown

		if ContextInfo.Vendor == Vendor.Nvidia:
			ContextInfo.MemoryAvailable = GL.glGetIntegerv(NvidiaIntegerName.GpuMemInfoTotalAvailable)
		
		ContextInfo.__Checked = True
		
	@staticmethod
	def PrintInfo():
		if not ContextInfo.__Checked:
			ContextInfo.TryGetInfo()
		
		print("-----GL INFO-----")
		print(f"Renderer: {ContextInfo.Renderer}")
		print(f"Vendor: {ContextInfo.Vendor}")
		print(f"Version: {ContextInfo.Version}")
		print(f"Shading language version: {ContextInfo.GLSLVersion}")
		if ContextInfo.MemoryAvailable != 0:
			print(f"Total video memory: {ContextInfo.MemoryAvailable / 1000000.0}GB")
		else:
			print("Total video memory: unavailable.")
	
	@staticmethod
	def GetVideoMemoryCurrent():
		if ContextInfo.Vendor == Vendor.Nvidia:
			return GL.glGetIntegerv(NvidiaIntegerName.GpuMemInfoCurrentAvailable)
		else:
			return 0