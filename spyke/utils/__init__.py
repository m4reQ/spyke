from __future__ import annotations
from .deletable import Deletable
from .math import *
from .windows import *
from spyke import debug
from typing import Callable, Sequence, List, TypeVar, Iterator as _Iterator
from types import ModuleType
from os import path
import time
import gc
import ctypes as ct
import inspect
import logging

__all__ = [
    'lerp_float',
    'lerp_vector',
    'create_translation',
    'create_scale',
    'create_rotation_x',
    'create_rotation_y',
    'create_rotation_z',
    'create_transform_3d',
    'garbage_collect',
    'pointer',
    'get_closest_factors',
    'get_known_folder_path',
    'get_extension_name',
    'get_submodules',
    'debug_only',
    'Iterator',
    'Delayer',
    'Vector2',
    'Vector3',
    'Vector4',
    'Matrix4',
    'Deletable'
]

pointer = ct.pointer

_LOGGER = logging.getLogger(__name__)

def get_submodules(module: ModuleType) -> List[ModuleType]:
    return [x[1] for x in inspect.getmembers(module, lambda x: inspect.ismodule(x))]

def get_extension_name(filepath: str) -> str:
    '''
    Returns extension of the file in form of uppercase file
    suffix with dot removed.
    '''

    return path.splitext(filepath)[1].removeprefix('.').upper()

def garbage_collect():
    prev = gc.get_count()[0]
    gc.collect()

    _LOGGER.debug('Garbage collection freed %d objects', prev - gc.get_count()[0])

def debug_only(func: Callable[..., None]) -> Callable[..., None]:
    '''
    Decorator function that allows a function to only be called
    while running with `__debug__ == True`. Else function call
    is simply omitted.
    To make sure there are no further complications with values not being returned
    if debug mode is on, it only accepts functions that does not return any value.

    @func: A function to be decorated.
    '''
    
    def inner(*args, **kwargs) -> None:
        if __debug__:
            func(*args, **kwargs)
    
    return inner

def create_quad_indices(quadsCount: int) -> List[int]:
    data = []

    offset = 0
    i = 0
    while i < quadsCount:
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

Iterable_T = TypeVar('Iterable_T')
class Iterator(_Iterator[Iterable_T]):
    __slots__ = (
        '__weakref__',
        '_iterable',
        '_last_pos',
        '_current',
        'looping'
    )

    def __init__(self, iterable: Sequence[Iterable_T], *, looping: bool = False):
        self._iterable = iterable
        self._last_pos = 0
        self._current = self._iterable[0]
        self.looping = looping

    def __next__(self) -> Iterable_T:
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
    def current(self) -> Iterable_T:
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

        curTime = time.perf_counter()

        self._to_wait -= curTime - self._last_time
        self._last_time = curTime

        return True
