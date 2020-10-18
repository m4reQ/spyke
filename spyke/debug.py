from . import DEBUG_ENABLE, START_TIME, DEBUG_LOG_TIME, IS_NVIDIA, DEBUG_COLOR
from .enums import StringName, ErrorCode, NvidiaIntegerName

from OpenGL.GL import glGetError, glGetString, glGetIntegerv, glGetStringi, GL_NUM_EXTENSIONS
import time
import colorama
import psutil
import os

if DEBUG_COLOR:
	colorama.init()

class LogLevel:
	Info = "INFO"
	Warning = "WARNING"
	Error = "ERROR"

LEVEL_COLOR_MAP = {
	LogLevel.Info: colorama.Fore.WHITE,
	LogLevel.Warning: colorama.Fore.YELLOW,
	LogLevel.Error: colorama.Fore.RED}

def __Log(msg: str, logLevel: LogLevel) -> None:
	print(f"[{logLevel}] {msg}")

def __LogTimed(msg: str, logLevel: LogLevel) -> None:
	print(f"[{logLevel}][{(time.perf_counter() - START_TIME):.3F}s] {msg}")

def __LogColored(msg: str, logLevel: LogLevel) -> None:
	print(f"{LEVEL_COLOR_MAP[logLevel]}[{logLevel}] {msg}{colorama.Style.RESET_ALL}")

def __LogTimedColored(msg: str, logLevel: LogLevel) -> None:
	print(f"{LEVEL_COLOR_MAP[logLevel]}[{logLevel}][{(time.perf_counter() - START_TIME):.3F}s] {msg}{colorama.Style.RESET_ALL}")

Log = lambda: None
if DEBUG_ENABLE:
	if DEBUG_COLOR:
		if DEBUG_LOG_TIME:
			Log = __LogTimedColored
		else:
			Log = __LogColored
	else:
		if DEBUG_LOG_TIME:
			Log = __LogTimed
		else:
			Log = __Log

__PROCESS = psutil.Process(os.getpid())

def GetGLError():
	err = glGetError()
	if err != ErrorCode.NoError:
		Log(err, LogLevel.Error)

def GetVideoMemoryCurrent():
	if IS_NVIDIA:
		return glGetIntegerv(NvidiaIntegerName.GpuMemInfoCurrentAvailable)
	else:
		return 1

def GetMemoryUsed():
	return __PROCESS.memory_info().rss

def EnsureString(string):
	if isinstance(string, str):
		return string
	
	return string.decode("ASCII")

class Timer:
	__Start = 0.0
	
	@staticmethod
	def Start():
		Timer.__Start = time.perf_counter()
	
	@staticmethod
	def Stop():
		return time.perf_counter() - Timer.__Start
	
	@staticmethod
	def GetCurrent():
		return time.perf_counter()

class GLInfo:
	Renderer = ""
	Vendor = ""
	Version = ""
	GLSLVersion = ""
	MemoryAvailable = 0

	__Checked = False

	@staticmethod
	def TryGetInfo():
		GLInfo.Renderer = EnsureString(glGetString(StringName.Renderer))
		GLInfo.Vendor = EnsureString(glGetString(StringName.Vendor))
		GLInfo.Version = EnsureString(glGetString(StringName.Version))
		GLInfo.GLSLVersion = EnsureString(glGetString(StringName.ShadingLanguageVersion))
		if IS_NVIDIA:
			GLInfo.MemoryAvailable = glGetIntegerv(NvidiaIntegerName.GpuMemInfoTotalAvailable)
		
		GLInfo.__Checked = True
		
	@staticmethod
	def PrintInfo():
		if not GLInfo.__Checked:
			GLInfo.TryGetInfo()
		
		print("-----GL INFO-----")
		print(f"Renderer: {GLInfo.Renderer}")
		print(f"Vendor: {GLInfo.Vendor}")
		print(f"Version: {GLInfo.Version}")
		print(f"Shading language version: {GLInfo.GLSLVersion}")
		if GLInfo.MemoryAvailable != 0:
			print(f"Total video memory available: {glGetIntegerv(NvidiaIntegerName.GpuMemInfoTotalAvailable) / 1000000.0}GB")
		else:
			print("Total video memory available: unavailable.")