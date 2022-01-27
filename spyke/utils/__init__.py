from typing import Sequence, List, TypeVar, Generator
import time
import gc

from .math import *
from spyke import debug

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
    'Iterator',
    'Delayer',
    'Vector2',
    'Vector3',
    'Vector4',
    'Matrix4'
]


def garbage_collect():
    prev = gc.get_count()[0]
    gc.collect()

    debug.log_info(
        f'Garbage collection freed {prev - gc.get_count()[0]} objects')


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


T = TypeVar('T')


class Iterator(Generator[T, None, None]):
    __slots__ = (
        '__weakref__',
        '_iterable',
        '_last_pos',
        '_current',
        'looping'
    )

    def __init__(self, iterable: Sequence[T], *, looping: bool = False):
        self._iterable = iterable
        self._last_pos = 0
        self._current = self._iterable[0]
        self.looping = looping

    def __next__(self) -> T:
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
    def current(self) -> T:
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
