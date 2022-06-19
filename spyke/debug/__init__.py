import colorama
import logging as _logging
import os
import sys
import ctypes as ct
import traceback
from OpenGL import GL

from spyke import paths
from .logging import SpykeLogger, LOG_LEVEL
from .decorators import timed, debug_only, require_context, profiled
from .opengl import opengl_debug_callback, get_gl_error
from .profiling import get_profiler, ChromeProfiler

__all__ = [
    'SpykeLogger',
    'LOG_LEVEL',
    'debug_only',
    'timed',
    'profiled',
    'require_context',
    'get_gl_error',
    'get_profiler',
    'ChromeProfiler'
]

def _exception_handler(_type, _, _traceback) -> None:
    logger = _logging.getLogger(__name__)
    exc_formatted = ''.join([_type.__name__, '\n', 'Traceback (most recent call last):\n'] + traceback.format_tb(_traceback))
    logger.error(exc_formatted)
    ct.windll.user32.MessageBoxW(
        None,
        f'A fatal error occured.\n{exc_formatted}',
        'Spyke error',
        0x10)
    sys.exit(1)

def init() -> None:
    colorama.init()

    _logging.basicConfig(level=LOG_LEVEL, handlers=[])
    _logging.setLoggerClass(SpykeLogger)

    if os.path.exists(paths.LOG_FILE):
        os.remove(paths.LOG_FILE)

    if not __debug__:
        sys.excepthook = _exception_handler

    _debug_proc = GL.GLDEBUGPROC(opengl_debug_callback)
    GL.glEnable(GL.GL_DEBUG_OUTPUT)
    GL.glEnable(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS)
    GL.glDebugMessageCallback(_debug_proc, None)

    _logger = _logging.getLogger(__name__)
    _logger.debug('Debug module initialized.')
