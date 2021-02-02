#region Import
from ..constants import DEBUG_ENABLE, DEBUG_COLOR, DEBUG_LOG_TIME, START_TIME, AUTO_LOG_EXCEPTIONS

from OpenGL import GL
import time
import colorama
import sys
#endregion

__GL_ERROR_CODE_NAMES_MAP = {
	0x0500: "INVALID_ENUM",
	0x0501: "INVALID_VALUE",
	0x0502: "INVALID_OPERATION",
	0x0503: "STACK_OVERFLOW",
	0x0504: "STACK_UNDERFLOW",
	0x0505: "OUT_OF_MEMORY",
	0x0506: "INVALID_FRAMEBUFFER_OPERATION",
	0x0507: "CONTEXT_LOST"}

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

if AUTO_LOG_EXCEPTIONS:
	sys.excepthook = lambda excType, val, _: Log(f"{type(excType).__name__}: {val}", LogLevel.Error)

def GetGLError():
	err = GL.glGetError()
	if err != GL.GL_NO_ERROR:
		Log(f"GLError: {__GL_ERROR_CODE_NAMES_MAP[err]} ({err})", LogLevel.Error)