import functools
import gc
import inspect
import logging
import os
import time
import typing as t
from types import ModuleType

from . import math
from .math import *

__all__ = [
    'garbage_collect',
    'get_extension_name',
    'get_submodules',
    'Iterator',
    'Delayer'] + math.__all__

_Iterable = t.TypeVar('_Iterable')
class Iterator(t.Iterator[_Iterable]):
    __slots__ = (
        '__weakref__',
        '_iterable',
        '_last_pos',
        '_current',
        'looping'
    )

    def __init__(self, iterable: t.Sequence[_Iterable], *, looping: bool = False):
        self._iterable = iterable
        self._last_pos = 0
        self._current = self._iterable[0]
        self.looping = looping

    def __next__(self) -> _Iterable:
        pos = self._last_pos
        self._last_pos += 1

        if self._last_pos >= len(self._iterable):
            if self.looping:
                self._last_pos = 0
            else:
                raise StopIteration

        self._current = self._iterable[pos]

        return self._current

    @property
    def current(self) -> _Iterable:
        return self._current

class Delayer:
    __slots__ = (
        '__weakref__',
        '_first_wait',
        '_wait_time',
        '_to_wait',
        '_last_time'
    )

    def __init__(self, wait_time: float):
        self._first_wait = True
        self._wait_time = wait_time
        self._to_wait = wait_time
        self._last_time = 0.0

    def is_waiting(self) -> bool:
        if self._first_wait:
            self._last_time = time.perf_counter()
            self._first_wait = False

        if self._to_wait <= 0.0:
            self._to_wait = self._wait_time
            return False

        cur_time = time.perf_counter()

        self._to_wait -= cur_time - self._last_time
        self._last_time = cur_time

        return True

def get_submodules(module: ModuleType) -> t.List[ModuleType]:
    return [x[1] for x in inspect.getmembers(module, inspect.ismodule)]

def get_extension_name(filepath: str) -> str:
    '''
    Returns extension of the file in form of uppercase file
    suffix with dot removed.
    '''

    return os.path.splitext(filepath)[1].removeprefix('.').upper()

_Params = t.ParamSpec('_Params')
_Return = t.TypeVar('_Return')
def once(f: t.Callable[_Params, _Return]) -> t.Callable[_Params, _Return]:
    '''
    Decorator that restricts decorated function to be called only once
    during program execution. Any further calls will result in an RuntimeError.

    @f: Function to be decorated.
    '''

    ran = False

    @functools.wraps(f)
    def inner(*args: _Params.args, **kwargs: _Params.kwargs) -> _Return:
        nonlocal ran
        if ran:
            raise RuntimeError(f'Function \"{f.__qualname__}\" can be called only once.')

        ran = True

        return f(*args, **kwargs)

    return inner

def garbage_collect():
    prev = gc.get_count()[0]
    gc.collect()

    _logger.debug('Garbage collection freed %d objects', prev - gc.get_count()[0])

@once
def create_quad_indices(quads_count: int) -> list[int]:
    data = []

    offset = 0
    i = 0
    while i < quads_count:
        data.extend([
            0 + offset,
            1 + offset,
            2 + offset,
            2 + offset,
            3 + offset,
            0 + offset])

        offset += 4
        i += 1

    return data

_logger = logging.getLogger(__name__)
