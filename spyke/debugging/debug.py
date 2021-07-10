from .logLevel import LogLevel
from ..exceptions import GraphicsException
from ..constants import DEFAULT_LOG_FILENAME, START_TIME, _GL_ERROR_CODE_NAMES_MAP, DEBUG_LOG_TO_FILE

import threading
import time
import colorama
import sys
from OpenGL import GL

Log = lambda _, __: None
GetGLError = lambda: None

_logFile = None

_screenlock = threading.RLock()
_fileLock = threading.RLock()

def TryCloseLogFile():
    try:
        _logFile.close()
    except Exception:
        pass

def _Log(msg: str, lvl: LogLevel) -> None:
    _str = f"[{lvl[0]}][{(time.perf_counter() - START_TIME):.3F}s] {msg}"

    _screenlock.acquire()
    print(str(lvl[1]) + _str + str(colorama.Style.RESET_ALL), end='\n')
    _screenlock.release()

    if DEBUG_LOG_TO_FILE:
        _fileLock.acquire()
        print(_str, end='\n', file=_logFile, flush=True)
        _fileLock.release()

def _GetGLError():
    err = GL.glGetError()
    if err != GL.GL_NO_ERROR:
        raise GraphicsException(f"GLError: {_GL_ERROR_CODE_NAMES_MAP[err]} ({err})")

def _Init():
    global Log, GetGLError, _logFile

    colorama.init()

    Log = _Log
    GetGLError = _GetGLError

    if DEBUG_LOG_TO_FILE:
        _logFile = open(DEFAULT_LOG_FILENAME, "w+")

    sys.excepthook = lambda excType, val, _: Log(f"{type(excType).__name__}: {val}", LogLevel.Error)