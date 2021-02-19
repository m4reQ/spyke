#region Import
from ..constants import START_TIME

from OpenGL import GL
import time
import colorama
import sys
#endregion

class LogLevel:
	Info = "INFO"
	Warning = "WARNING"
	Error = "ERROR"

__GL_ERROR_CODE_NAMES_MAP = {
	0x0500: "INVALID_ENUM",
	0x0501: "INVALID_VALUE",
	0x0502: "INVALID_OPERATION",
	0x0503: "STACK_OVERFLOW",
	0x0504: "STACK_UNDERFLOW",
	0x0505: "OUT_OF_MEMORY",
	0x0506: "INVALID_FRAMEBUFFER_OPERATION",
	0x0507: "CONTEXT_LOST"}

LEVEL_COLOR_MAP = {
	LogLevel.Info: colorama.Fore.WHITE,
	LogLevel.Warning: colorama.Fore.YELLOW,
	LogLevel.Error: colorama.Fore.RED}

SEVERITY_LEVEL_COLOR_MAP = {
	GL.GL_DEBUG_SEVERITY_HIGH: colorama.Fore.RED,
	GL.GL_DEBUG_SEVERITY_MEDIUM: colorama.Fore.YELLOW,
	GL.GL_DEBUG_SEVERITY_LOW: colorama.Fore.WHITE,
	GL.GL_DEBUG_SEVERITY_NOTIFICATION: colorama.Fore.WHITE}

Log = lambda _, __: None
GetGLError = lambda: None

# def _GL_DEBUG_PROC(source, _, __, severity, ___, message, ____):
# 	print(f"{SEVERITY_LEVEL_COLOR_MAP[severity]}[OPENGL][{(time.perf_counter() - START_TIME):.3F}s] {source} -> {message}{colorama.Style.RESET_ALL}")

def __LogTimedColored(msg: str, logLevel: LogLevel) -> None:
	print(f"{LEVEL_COLOR_MAP[logLevel]}[{logLevel}][{(time.perf_counter() - START_TIME):.3F}s] {msg}{colorama.Style.RESET_ALL}")

def __GetGLError():
	err = GL.glGetError()
	if err != GL.GL_NO_ERROR:
		Log(f"GLError: {__GL_ERROR_CODE_NAMES_MAP[err]} ({err})", LogLevel.Error)

def _Init():
	global Log, GetGLError
	
	colorama.init()
	
	Log = __LogTimedColored
	GetGLError = __GetGLError

	sys.excepthook = lambda excType, val, _: Log(f"{type(excType).__name__}: {val}", LogLevel.Error)