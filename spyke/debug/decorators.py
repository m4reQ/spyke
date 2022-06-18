import typing as t
import functools
import glfw
import logging
import time

from spyke.exceptions import GraphicsException

_RT = t.TypeVar('_RT')

def timed(func: t.Callable[..., _RT]) -> t.Callable[..., _RT]:
    '''
    A decorator function that enables profiling execution time of given
    callable. It automatically logs execution time and saves it to profile
    file if profiling is enabled. This decorator is only applied when running in debug mode.

    @func: A function to be decorated.
    '''

    @functools.wraps(func)
    def inner(*args, **kwargs):
        start = time.perf_counter()

        res = func(*args, **kwargs)

        _logger = logging.getLogger(__name__)
        _logger.debug('Function %s executed in %f seconds.', func.__qualname__, time.perf_counter() - start)

        return res

    if __debug__:
        return inner

    return func

def debug_only(func: t.Callable[..., None]) -> t.Callable[..., None]:
    '''
    Decorator function that allows a function to only be called
    while running with `__debug__ == True`. Else function call
    is simply omitted.
    To make sure there are no further complications with values not being returned
    if debug mode is on, it only accepts functions that does not return any value.

    @func: A function to be decorated.
    '''

    @functools.wraps(func)
    def inner(*args, **kwargs) -> None:
        if __debug__:
            func(*args, **kwargs)

    return inner

def check_context(func: t.Callable[..., _RT]) -> t.Callable[..., _RT]:
    '''
    Decorator function which indicates that decorated function
    can only be called with present OpenGL context. Otherwise it raises
    an exception. This decorator is only applied when running in debug mode.

    @func: A function to be decorated.
    '''

    @functools.wraps(func)
    def inner(*args, **kwargs) -> _RT:
        if glfw.get_current_context() is None:
            # TODO: Create NoContextException class
            raise GraphicsException('Required OpenGL context but no context is set current.')

        return func(*args, **kwargs)

    if __debug__:
        return inner

    return func
