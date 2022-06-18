import typing as t
import time
import gc
import ctypes as ct
import inspect
import logging
from os import path
from types import ModuleType

from .deletable import Deletable
from .math import *

from . import math

__all__ = [
    'garbage_collect',
    'pointer',
    'get_extension_name',
    'get_submodules',
    'Iterator',
    'Delayer',
    'Deletable'
]
__all__ += math.__all__

pointer = ct.pointer

_logger = logging.getLogger(__name__)

def get_submodules(module: ModuleType) -> t.List[ModuleType]:
    return [x[1] for x in inspect.getmembers(module, inspect.ismodule)]

def get_extension_name(filepath: str) -> str:
    '''
    Returns extension of the file in form of uppercase file
    suffix with dot removed.
    '''

    return path.splitext(filepath)[1].removeprefix('.').upper()

def garbage_collect():
    prev = gc.get_count()[0]
    gc.collect()

    _logger.debug('Garbage collection freed %d objects', prev - gc.get_count()[0])

def create_quad_indices(quads_count: int) -> t.List[int]:
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

T_Iterable = t.TypeVar('T_Iterable')
class Iterator(t.Iterator[T_Iterable]):
    __slots__ = (
        '__weakref__',
        '_iterable',
        '_last_pos',
        '_current',
        'looping'
    )

    def __init__(self, iterable: t.Sequence[T_Iterable], *, looping: bool = False):
        self._iterable = iterable
        self._last_pos = 0
        self._current = self._iterable[0]
        self.looping = looping

    def __next__(self) -> T_Iterable:
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
    def current(self) -> T_Iterable:
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
