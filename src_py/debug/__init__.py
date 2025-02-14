import logging
import os
import typing as t

import colorama

from spyke import paths

from ._logging import LOG_LEVEL, SpykeLogger
from .profiling import (begin_profiling_frame, begin_profiling_session,
                        emit_profiling_event, end_profiling_frame,
                        end_profiling_session, update_profiling_counter)

__all__ = [
    'debug_only',
    'profiled',
    'profiled_scope',
    'begin_profiling_frame',
    'emit_profiling_event',
    'end_profiling_session',
    'begin_profiling_session',
    'end_profiling_frame',
    'update_profiling_counter']

TParams = t.ParamSpec('TParams')
TReturn = t.TypeVar('TReturn')

class _ProfiledScope:
    def __init__(self, name: str) -> None:
        self._name = name
        self._start = 0

    def __enter__(self) -> t.Self:
        self._start = begin_profiling_frame()
        return self

    def __exit__(self, *_) -> None:
        end_profiling_frame(self._start, self._name)

def profiled_scope(name: str) -> _ProfiledScope:
    return _ProfiledScope(name)

def profiled(func: t.Callable[TParams, TReturn]) -> t.Callable[TParams, TReturn]:
    '''
    A decorator function that enables profiling execution of given
    callable. It automatically logs execution time and saves it to profile
    file. This decorator is only applied when running in debug mode.
    '''

    def inner(*args: TParams.args, **kwargs: TParams.kwargs) -> TReturn:
        start = begin_profiling_frame()
        res = func(*args, **kwargs)
        end_profiling_frame(start, f'{func.__module__}:{func.__qualname__}')

        return res

    return inner if __debug__ else func

def debug_only(func: t.Callable[TParams, None]) -> t.Callable[TParams, None]:
    '''
    Decorator function that allows a function to only be called
    while running with `__debug__ == True`. Else function call
    is simply omitted.
    To make sure there are no further complications with values not being returned
    if debug mode is on, it only accepts functions that does not return any value.

    @func: A function to be decorated.
    '''

    return func if __debug__ else (lambda *args, **kwargs: None)

def initialize() -> None:
    colorama.init()

    logging.basicConfig(level=LOG_LEVEL, handlers=[])
    logging.setLoggerClass(SpykeLogger)

    if os.path.exists(paths.LOG_FILE):
        os.remove(paths.LOG_FILE)

    _logger = logging.getLogger(__name__)
    _logger.info('Spyke debug module initialized.')
