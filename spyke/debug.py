from typing import Callable
from spyke.exceptions import GraphicsException
import glfw
import logging
import colorama
import os
import time
import sys
from OpenGL import GL

LOG_FILE = 'nova_log.log'

_log_levels = {
    'SP_INFO': logging.DEBUG + 1,
    'SP_OK': logging.DEBUG + 2,
    'SP_WARNING': logging.DEBUG + 3,
    'SP_ERROR': logging.DEBUG + 4,
}

for name, lvl in _log_levels.items():
    logging.addLevelName(lvl, name)
    setattr(logging, name, lvl)


class _FileFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(fmt='[%(levelname)s][%(asctime)s] %(message)s')

    def format(self, record: logging.LogRecord) -> str:
        formatter = logging.Formatter(self._fmt)

        return formatter.format(record)


class _ConsoleFormatter(logging.Formatter):
    _color_map = {
        logging.SP_INFO: colorama.Fore.WHITE,
        logging.SP_OK: colorama.Fore.GREEN,
        logging.SP_WARNING: colorama.Fore.YELLOW,
        logging.SP_ERROR: colorama.Fore.RED
    }

    _style_reset = colorama.Style.RESET_ALL

    def __init__(self):
        super().__init__(fmt='[%(levelname)s] %(message)s')

    def format(self, record: logging.LogRecord) -> str:
        fmt = _ConsoleFormatter._color_map[record.levelno] + \
            self._fmt + _ConsoleFormatter._style_reset
        formatter = logging.Formatter(fmt)

        return formatter.format(record)


def _init_logging() -> None:
    colorama.init()

    if os.path.isfile(LOG_FILE):
        open(LOG_FILE, 'w').close()

    _file_handler = logging.FileHandler(LOG_FILE, mode='w+')
    _file_handler.setLevel(logging.SP_INFO)
    _file_handler.setFormatter(_FileFormatter())

    _con_handler = logging.StreamHandler(sys.stdout)
    _con_handler.setLevel(logging.SP_INFO)
    _con_handler.setFormatter(_ConsoleFormatter())

    logging.basicConfig(
        level=logging.SP_INFO,
        handlers=[
            _con_handler,
            _file_handler,
        ],
        force=True
    )


if __debug__:
    _init_logging()


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

        logging.log(
            logging.SP_INFO, f'Function {func.__qualname__} executed in {time.perf_counter() - start} seconds.')

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
