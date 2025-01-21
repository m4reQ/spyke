import functools
import logging as _logging
import os
import typing as t

import colorama

from spyke import paths
from spyke.debug.logging import LOG_LEVEL, SpykeLogger
from spyke.debug.profiling import profiled, profiled_scope

__all__ = [
    'SpykeLogger',
    'LOG_LEVEL',
    'debug_only',
    'profiled',
    'profiled_scope',
    'get_profiler',
    'ChromeProfiler',
    'profiler',
]

_Params = t.ParamSpec('_Params')

def debug_only(func: t.Callable[_Params, None]) -> t.Callable[_Params, None]:
    '''
    Decorator function that allows a function to only be called
    while running with `__debug__ == True`. Else function call
    is simply omitted.
    To make sure there are no further complications with values not being returned
    if debug mode is on, it only accepts functions that does not return any value.

    @func: A function to be decorated.
    '''

    @functools.wraps(func)
    def inner(*args: _Params.args, **kwargs: _Params.kwargs) -> None:
        if __debug__:
            func(*args, **kwargs)

    return inner

def initialize() -> None:
    colorama.init()

    _logging.basicConfig(level=LOG_LEVEL, handlers=[])
    _logging.setLoggerClass(SpykeLogger)

    if os.path.exists(paths.LOG_FILE):
        os.remove(paths.LOG_FILE)

    _logger = _logging.getLogger(__name__)
    _logger.info('Spyke debug module initialized.')

