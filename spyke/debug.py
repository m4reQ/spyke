from typing import Callable
from spyke.exceptions import GraphicsException
import glfw
import logging
import colorama
import os
import time
from OpenGL import GL

LOG_FILE = 'nova_log.log'


class ConsoleFormatter(logging.Formatter):
    ColorMap = {
        logging.DEBUG: colorama.Fore.WHITE,
        logging.INFO: colorama.Fore.WHITE,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED
    }

    StyleReset = colorama.Style.RESET_ALL

    def __init__(self):
        super().__init__()

        self.fmt = '[%(levelname)s] %(message)s'

    def format(self, record: logging.LogRecord) -> str:
        fmt = self.ColorMap[record.levelno] + self.fmt + self.StyleReset
        formatter = logging.Formatter(fmt)

        return formatter.format(record)


class FileFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

        self.fmt = '[%(levelname)s][%(asctime)s] %(message)s'

    def format(self, record: logging.LogRecord) -> str:
        formatter = logging.Formatter(self.fmt)

        return formatter.format(record)


colorama.init()

if os.path.isfile(LOG_FILE):
    open(LOG_FILE, 'w').close()

_logger = logging.getLogger()
_logger.setLevel(logging.INFO)

_file_handler = logging.FileHandler(LOG_FILE)
_file_handler.setLevel(logging.INFO)
_file_handler.setFormatter(FileFormatter())
_logger.addHandler(_file_handler)

_con_handler = logging.StreamHandler()
_con_handler.setLevel(logging.INFO)
_con_handler.setFormatter(ConsoleFormatter())
_logger.addHandler(_con_handler)


def log_info(msg: str) -> None:
    if __debug__:
        _logger.info(msg)


def log_warning(msg: str) -> None:
    if __debug__:
        _logger.warning(msg)


def log_error(msg: str, log_info: bool = True) -> None:
    if __debug__:
        _logger.error(msg, log_info)


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

        log_info(
            f'Function {func.__qualname__} executed in {time.perf_counter() - start} seconds.')

        return res

    return inner


def check_context() -> None:
    '''
    Checks if OpenGL context has been set. If not raises
    GraphicsException.
    '''

    if not __debug__:
        return

    if glfw.get_current_context() is None:
        raise GraphicsException(
            'Required OpenGL context but no context was made current.')
