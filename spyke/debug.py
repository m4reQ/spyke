from . import DEBUG_ENABLE, START_TIME, DEBUG_LOG_TIME, IS_NVIDIA, DEBUG_COLOR
from .enums import StringName, ErrorCode, NvidiaIntegerName

from OpenGL.GL import glGetError, glGetString, glGetIntegerv, glGetStringi, GL_NUM_EXTENSIONS
import time
import colorama

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

def GetGLError():
	err = glGetError()
	if err != ErrorCode.NoError:
		Log(err, LogLevel.Error)

def GetGLInfo():
	print("-----INFO-----")
	print(f"Renderer: {glGetString(StringName.Renderer).decode()}")
	print(f"Vendor: {glGetString(StringName.Vendor).decode()}")
	print(f"Version: {glGetString(StringName.Version).decode()}")
	print(f"Shading language version: {glGetString(StringName.ShadingLanguageVersion).decode()}")

	if IS_NVIDIA:
		print(f"Total video memory available: {glGetIntegerv(NvidiaIntegerName.GpuMemInfoTotalAvailable) / 1000000.0}GB")

def GetVideoMemoryAvailable():
	if IS_NVIDIA:
		return glGetIntegerv(NvidiaIntegerName.GpuMemInfoTotalAvailable)
	else:
		return 1

def GetVideoMemoryCurrent():
	if IS_NVIDIA:
		return glGetIntegerv(NvidiaIntegerName.GpuMemInfoCurrentAvailable)
	else:
		return 1

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