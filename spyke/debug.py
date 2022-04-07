from __future__ import annotations
from spyke.enums import DebugSeverity, DebugSource, DebugType
from spyke.exceptions import GraphicsException
from spyke.utils import debug_only
from OpenGL import GL
import glfw
import logging
import colorama
import os

LOG_LEVEL: int = logging.DEBUG if __debug__ else logging.WARNING
LOG_FILE: str = os.path.join('.', 'spyke_log.log')
_DEBUG_PROC = None

class _ConsoleFormatter(logging.Formatter):
    _color_map = {
        logging.DEBUG: colorama.Fore.WHITE,
        logging.INFO: colorama.Fore.WHITE,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.FATAL: colorama.Back.WHITE + colorama.Fore.RED
    }

    def format(self, record: logging.LogRecord) -> str:
        return self._color_map.get(record.levelno, '') + super().format(record) + colorama.Style.RESET_ALL

class _SpykeLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith('spyke') and super().filter(record)

class _SpykeLogger(logging.Logger):
    _log_format: str = '[%(levelname)s][%(asctime)s.%(msecs)03d] (%(threadName)s) %(name)s: %(message)s'
    _log_time_format: str = '%H:%M:%S'

    def __init__(self, name: str):
        super().__init__(name, LOG_LEVEL)

        _file_handler = logging.FileHandler(LOG_FILE)
        _file_handler.setLevel(LOG_LEVEL)
        _file_handler.setFormatter(logging.Formatter(
            fmt=self._log_format,
            datefmt=self._log_time_format
            ))
        self.addHandler(_file_handler)

        _con_handler = logging.StreamHandler()
        _con_handler.setLevel(LOG_LEVEL)
        _con_handler.setFormatter(_ConsoleFormatter(
            fmt=self._log_format,
            datefmt=self._log_time_format
            ))
        self.addHandler(_con_handler)

        self.addFilter(_SpykeLogFilter(name))

        self.propagate = False

def _opengl_debug_callback(source: int, msg_type: int, _, severity: int, __, raw: bytes, ___) -> None:
    logger = logging.getLogger(__name__)

    _source = DebugSource(source).name.upper()
    _msg_type = DebugType(msg_type).name.upper()
    _severity = DebugSeverity(severity)

    message_formatted = f'OpenGL {_source} -> {_msg_type}: {raw.decode("ansi")}.'

    if _severity == DebugSeverity.High:
        raise GraphicsException(message_formatted)
    elif _severity == DebugSeverity.Medium:
        logger.warning(message_formatted)
    elif _severity in [DebugSeverity.Low, DebugSeverity.Notification]:
        logger.info(message_formatted)

@debug_only
def get_gl_error() -> None:
    err = GL.glGetError()
    if err != GL.GL_NO_ERROR:
        raise GraphicsException(err)

@debug_only
def check_context() -> None:
    '''
    Checks if OpenGL context has been set. If not raises
    `GraphicsException`.
    '''

    assert glfw.get_current_context() is not None, 'Required OpenGL context but no context is set current.'

@debug_only
def _init() -> None:
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    colorama.init()
    logging.basicConfig(level=LOG_LEVEL, handlers=[])
    logging.setLoggerClass(_SpykeLogger)

    global _DEBUG_PROC
    if _DEBUG_PROC is not None:
        return

    _DEBUG_PROC = GL.GLDEBUGPROC(_opengl_debug_callback)    
    GL.glEnable(GL.GL_DEBUG_OUTPUT)
    GL.glEnable(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS)
    GL.glDebugMessageCallback(_DEBUG_PROC, None)

    logger = logging.getLogger(__name__)
    logger.debug('Debug module initialized.')