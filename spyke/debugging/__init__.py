#region Import
from ..constants import START_TIME, DEFAULT_LOG_FILENAME, _GL_ERROR_CODE_NAMES_MAP
from ..exceptions import GraphicsException

from OpenGL import GL
import time
import colorama
import sys
#endregion

class LogLevel:
	Info = "INFO"
	Warning = "WARN"
	Error = "ERROR"

_LEVEL_COLOR_MAP = {
	LogLevel.Info:		colorama.Fore.WHITE,
	LogLevel.Warning:	colorama.Fore.YELLOW,
	LogLevel.Error: 	colorama.Fore.RED
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
			raise GraphicsException(f"GLError: {_GL_ERROR_CODE_NAMES_MAP[err]} ({err})")
	
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