#temporarily placed here to avoid circular import between imgui-debug-utils.compat 
def _EnsureString(string):
	if isinstance(string, str):
		return string
	
	return string.decode("ASCII")

from . import DEBUG_ENABLE, START_TIME, DEBUG_LOG_TIME, IS_NVIDIA, DEBUG_COLOR, AUTO_LOG_EXCEPTIONS, _PROCESS
from .enums import StringName, ErrorCode, NvidiaIntegerName

from OpenGL.GL import glGetError, glGetString, glGetIntegerv, GL_NUM_EXTENSIONS
import time
import colorama
import sys

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

Log = lambda _, __: None
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

def __ExcHook(excType, value, _):
	Log(f"{type(excType).__name__}: {value}", LogLevel.Error)

if AUTO_LOG_EXCEPTIONS:
	sys.excepthook = __ExcHook

def GetGLError():
	err = glGetError()
	if err != ErrorCode.NoError:
		Log(f"GLError: {err}", LogLevel.Error)

def GetVideoMemoryCurrent():
	if IS_NVIDIA:
		return glGetIntegerv(NvidiaIntegerName.GpuMemInfoCurrentAvailable)
	else:
		return 0

def GetMemoryUsed():
	return _PROCESS.memory_info().rss

class GLInfo:
	Renderer = ""
	Vendor = ""
	Version = ""
	GLSLVersion = ""
	MemoryAvailable = 0

	__Checked = False

	@staticmethod
	def TryGetInfo():
		GLInfo.Renderer = _EnsureString(glGetString(StringName.Renderer))
		GLInfo.Vendor = _EnsureString(glGetString(StringName.Vendor))
		GLInfo.Version = _EnsureString(glGetString(StringName.Version))
		GLInfo.GLSLVersion = _EnsureString(glGetString(StringName.ShadingLanguageVersion))
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
			print(f"Total video memory: {glGetIntegerv(NvidiaIntegerName.GpuMemInfoTotalAvailable) / 1000000.0}GB")
		else:
			print("Total video memory: unavailable.")