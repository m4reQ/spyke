from __future__ import annotations

import ctypes as ct
import logging
import sys
import traceback
import typing as t

from spyke.enums import ErrorCode
from spyke.utils import once

if t.TYPE_CHECKING:
    from spyke.enums import FramebufferStatus

__all__ = [
    'GraphicsException',
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

class GraphicsException(SpykeException):
    '''
    Represents graphics related exceptions.
    '''

    __module__ = ''

    @t.overload
    def __init__(self, error: str) -> None: ...

    @t.overload
    def __init__(self, error: ErrorCode) -> None: ...

    @t.overload
    def __init__(self, error: int) -> None: ...

    def __init__(self, error: str | ErrorCode | int) -> None:
        error_str = ''

        if isinstance(error, ErrorCode):
            error_str = f'OpenGL error: {error.name} ({error.value})'
        elif isinstance(error, int):
            error_str = f'OpenGL error: {ErrorCode(error).name} ({error})'
        elif isinstance(error, str):
            error_str = error
        else:
            raise TypeError(f'Invalid argument type for "error": {type(error)}.')

        super().__init__(error_str)

class NoContextException(GraphicsException):
    '''
    Raised when no graphics context is set current.
    '''

    __module__ = ''

    def __init__(self) -> None:
        super().__init__('OpenGL context is not set.')

class BufferOverflowException(GraphicsException):
    __module__ = ''

    def __init__(self, buffer_id: int, nbytes: int) -> None:
        super().__init__(f'Transfer of {nbytes} bytes to buffer with id {buffer_id} would cause buffer overflow.')

class ExtensionNotPresent(GraphicsException):
    __module__ = ''

    def __init__(self, ext_name: str) -> None:
        super().__init__(f'Required extension {ext_name} is not supported by this machine.')

class RendererNotInitializedException(GraphicsException):
    __module__ = ''

    def __init__(self) -> None:
        super().__init__('Renderer is not initialized.')

class FramebufferIncompleteException(GraphicsException):
    __module__ = ''

    def __init__(self, status: FramebufferStatus) -> None:
        super().__init__(f'Framebuffer is incomplete: {status.name}.')

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
