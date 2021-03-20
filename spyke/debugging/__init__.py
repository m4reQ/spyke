#region Import
from ..constants import START_TIME, DEFAULT_LOG_FILENAME
from ..exceptions import GraphicsException

from OpenGL import GL
import time
import colorama
import sys
#endregion

_GL_ERROR_CODE_NAMES_MAP = {
	GL.GL_INVALID_ENUM: "INVALID_ENUM",
	GL.GL_INVALID_VALUE: "INVALID_VALUE",
	GL.GL_INVALID_OPERATION: "INVALID_OPERATION",
	GL.GL_STACK_OVERFLOW: "STACK_OVERFLOW",
	GL.GL_STACK_UNDERFLOW: "STACK_UNDERFLOW",
	GL.GL_OUT_OF_MEMORY: "OUT_OF_MEMORY",
	GL.GL_INVALID_FRAMEBUFFER_OPERATION: "INVALID_FRAMEBUFFER_OPERATION",
	GL.GL_CONTEXT_LOST: "CONTEXT_LOST"}

_GL_FB_ERROR_CODE_NAMES_MAP = {
	GL.GL_FRAMEBUFFER_UNDEFINED: "FRAMEBUFFER_UNDEFINED",
	GL.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: "INCOMPLETE_ATTACHMENT",
	GL.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: "INCOMPLETE_MISSING_ATTACHMENT",
	GL.GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER: "FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER",
	GL.GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER: "FRAMEBUFFER_INCOMPLETE_READ_BUFFER"
}

class LogLevel:
	Info = "INFO"
	Warning = "WARNING"
	Error = "ERROR"

_LEVEL_COLOR_MAP = {
	LogLevel.Info: colorama.Fore.WHITE,
	LogLevel.Warning: colorama.Fore.YELLOW,
	LogLevel.Error: colorama.Fore.RED
}

class Debug:
	Log = lambda _, __: None
	GetGLError = lambda: None

	__LogFile = None

	def LogImpl(msg: str, lvl: LogLevel) -> None:
		global _LEVEL_COLOR_MAP

		_str = f"[{lvl}][{(time.perf_counter() - START_TIME):.3F}s] {msg}"

		print(str(_LEVEL_COLOR_MAP[lvl]) + _str + str(colorama.Style.RESET_ALL))
		Debug.WriteToLogFile(_str)

	def GetGLErrorImpl():
		global _GL_ERROR_CODE_NAMES_MAP

		err = GL.glGetError()
		if err != GL.GL_NO_ERROR:
			ex = GraphicsException(f"GLError: {_GL_ERROR_CODE_NAMES_MAP[err]} ({err})")
			raise ex
	
	def WriteToLogFile(msg):
		Debug.__LogFile.write(msg + "\n")
		Debug.__LogFile.flush()
	
	def CloseLogFile():
		Debug.__LogFile.close()
	
	def _Init():
		colorama.init()
	
		Debug.Log = Debug.LogImpl
		Debug.GetGLError = Debug.GetGLErrorImpl

		Debug.__LogFile = open(DEFAULT_LOG_FILENAME, "w+")

		sys.excepthook = lambda excType, val, _: Debug.Log(f"{type(excType).__name__}: {val}", LogLevel.Error)