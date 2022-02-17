from typing import Callable
from spyke.enums import DebugSeverity, DebugSource, DebugType
from spyke.exceptions import GraphicsException
import glfw
import logging
import colorama
import os
import time
import sys
from OpenGL import GL


LOG_FILE = 'nova_log.log'


colorama.init()


class _FileFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt='[%(levelname)s][%(asctime)s] %(message)s')

    def format(self, record: logging.LogRecord) -> str:
        formatter = logging.Formatter(self._fmt)

        return formatter.format(record)


class _ConsoleFormatter(logging.Formatter):
    _color_map = {
        logging.INFO: colorama.Fore.WHITE,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
    }

    _style_reset = colorama.Style.RESET_ALL

    def __init__(self):
        super().__init__(fmt='[%(levelname)s] %(message)s')

    def format(self, record: logging.LogRecord) -> str:
        fmt = _ConsoleFormatter._color_map[record.levelno] + \
            self._fmt + _ConsoleFormatter._style_reset
        formatter = logging.Formatter(fmt)

        return formatter.format(record)


class _SpykeLogger(logging.Logger):
    def __init__(self):
        super().__init__('SpykeLogger')

        _file_handler = logging.FileHandler(LOG_FILE, mode='w+')
        _file_handler.setLevel(logging.INFO)
        _file_handler.setFormatter(_FileFormatter())

        _con_handler = logging.StreamHandler(sys.stdout)
        _con_handler.setLevel(logging.INFO)
        _con_handler.setFormatter(_ConsoleFormatter())

        self.addHandler(_file_handler)
        self.addHandler(_con_handler)


if os.path.isfile(LOG_FILE):
    open(LOG_FILE, 'w').close()


_logger = _SpykeLogger()


def _opengl_debug_callback(source: int, msg_type: int, _, severity: int, __, raw: bytes, ___) -> None:
    _source = DebugSource(source).name.upper()
    _msg_type = DebugType(msg_type).name.upper()
    _severity = DebugSeverity(severity)

    message_formatted = f'OpenGL {_source} -> {_msg_type}: {raw.decode("ansi")}.'

    if _severity == DebugSeverity.High:
        raise GraphicsException(message_formatted)
    elif _severity == DebugSeverity.Medium:
        log_warning(message_formatted)
    elif _severity in [DebugSeverity.Low, DebugSeverity.Notification]:
        log_info(message_formatted)


_debug_proc = GL.GLDEBUGPROC(_opengl_debug_callback)


def enable_opengl_debug() -> None:
    GL.glEnable(GL.GL_DEBUG_OUTPUT)
    GL.glEnable(GL.GL_DEBUG_OUTPUT_SYNCHRONOUS)
    GL.glDebugMessageCallback(_debug_proc, None)


def log_info(msg: object) -> None:
    if __debug__:
        _logger.info(msg)


def log_warning(msg: object) -> None:
    if __debug__:
        _logger.warning(msg)


def log_error(msg: object) -> None:
    if __debug__:
        _logger.error(msg)


def get_gl_error():
    if not __debug__:
        return

    err = GL.glGetError()
    if err != GL.GL_NO_ERROR:
        raise GraphicsException(err)


def get_bound_texture(unit: int) -> int:
    if not __debug__:
        return -1

    GL.glActiveTexture(GL.GL_TEXTURE0 + unit)
    return GL.glGetInteger(GL.GL_TEXTURE_BINDING_2D)


def timed(func: Callable) -> Callable:
    def inner(*args, **kwargs):
        if not __debug__:
            return func(*args, **kwargs)

        start = time.perf_counter()
        res = func(*args, **kwargs)

        log_info(f'Function {func.__qualname__} executed in {time.perf_counter() - start} seconds.')

        return res

    return inner


def check_context() -> None:
    '''
    Checks if OpenGL context has been set. If not raises
    GraphicsException.
    '''

    assert glfw.get_current_context() is not None, 'Required OpenGL context but no context is set current.'