from __future__ import annotations

import ctypes as ct
import logging
import sys
import traceback
import typing as t

from spyke.utils import once

__all__ = [
    'SpykeException',
    'NoContextException'
]

@once
def initialize() -> None:
    if not __debug__:
        sys.excepthook = exception_hook

class SpykeException(RuntimeError):
    '''
    Represents exceptions that come from spyke library.
    '''

    __module__ = ''

    def __init__(self, message: str) -> None:
        super().__init__(message)

class LoaderNotFoundException(SpykeException):
    __module__ = ''

    def __init__(self, extension: str) -> None:
        super().__init__(f'Resource loader for extension {extension} not found.')

def exception_hook(_type, _, _traceback) -> None:
    logger = logging.getLogger(__name__)
    exc_formatted = ''.join([_type.__name__, '\n', 'Traceback (most recent call last):\n'] + traceback.format_tb(_traceback))
    logger.error(exc_formatted)
    ct.windll.user32.MessageBoxW(
        None,
        f'A fatal error occured.\n{exc_formatted}',
        'Spyke error',
        0x10)
    sys.exit(1)
