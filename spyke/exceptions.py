from __future__ import annotations
from spyke.enums import ErrorCode
from typing import Union
import sys
import ctypes as ct
import traceback
import logging

__all__ = [
    'GraphicsException',
    'SpykeException',
]

class GraphicsException(Exception):
    __module__ = ''

    def __init__(self, error: Union[str, ErrorCode, int]):
        error_str = ''

        if isinstance(error, ErrorCode):
            error_str = f'OpenGL error: {error.name} ({error.value})'
        elif isinstance(error, int):
            error_str = f'OpenGL error: {ErrorCode(error).name} ({error})'
        elif isinstance(error, str):
            error_str = error
        else:
            raise TypeError(
                f'Invalid argument type for "error": {type(error)}.')

        super().__init__(error_str)

class SpykeException(Exception):
    __module__ = ''

    def __init__(self, message: str):
        super().__init__(message)

def _exception_handler(_type, _, _traceback) -> None:
    logger = logging.getLogger(__name__)
    exc_formatted = ''.join([_type.__name__, '\n', 'Traceback (most recent call last):\n'] + traceback.format_tb(_traceback))
    logger.error(exc_formatted)
    ct.windll.user32.MessageBoxW(
        None, f'A fatal error occured.\n{exc_formatted}', 'Spyke error', 0x10)
    sys.exit(1)

if not __debug__:
    sys.excepthook = _exception_handler