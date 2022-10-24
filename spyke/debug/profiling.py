import dataclasses
import functools
import io
import json
import logging
import os
import threading
import time
import typing as t

from spyke import paths, runtime
from spyke.utils import once

_MAX_FRAMES = 400
_HEADER = '{"traceEvents":['
_FOOTER = ']}'
_RT = t.TypeVar('_RT')
_AT = t.ParamSpec('_AT')
_FRAME_FORMAT = '{"name": "{}", "cat": "{}", "ph": "{}", "ts": {}, "tid": {}, "pid": {}}'

def _create_frame_data(
    func_name: str,
    thread_id: int,
    process_id: int,
    categories: str,
    start: int,
    end: int) -> str:
    return _FRAME_FORMAT.format(func_name, ','.join(categories), 'B', _to_microseconds(start), thread_id, process_id) \
        + ',' \
        + _FRAME_FORMAT.format(func_name, ','.join(categories), 'E', _to_microseconds(end), thread_id, process_id)

@dataclasses.dataclass
class _ProfileFrame:
    name: str
    time_start: float
    time_end: float
    thread_id: int = dataclasses.field(default_factory=threading.get_ident)
    process_id: int = dataclasses.field(default_factory=os.getpid)
    categories: t.Iterable[str] = dataclasses.field(default_factory=list)

    @property
    def begin_event(self) -> dict[str, t.Any]:
        return {
            'name': self.name,
            'cat': ','.join(self.categories),
            'ph': 'B',
            'ts': self.time_start,
            'tid': self.thread_id,
            'pid': self.process_id}

    @property
    def end_event(self) -> dict[str, t.Any]:
        return {
            'name': self.name,
            'cat': ','.join(self.categories),
            'ph': 'E',
            'ts': self.time_end,
            'tid': self.thread_id,
            'pid': self.process_id}

    def dump(self, file: t.TextIO) -> None:
        json.dump(self.begin_event, file)
        file.write(',')
        json.dump(self.end_event, file)
        file.write(',')

@once
def initialize() -> None:
    with _write_lock:
        _file.write(_HEADER)
        _file.flush()

    runtime.register_dispose_function(_close_profiler)

def profile(func: t.Callable,
            start: int,
            end: int,
            categories: t.Iterable[str]) -> None:
    if len(_frames) >= _MAX_FRAMES:
        runtime.submit_future(_dump_frames, _frames.copy())
        _frames.clear()

    # _frames.append(_create_frame_data(func,))
    # frame = _ProfileFrame(
    #     func.__qualname__,
    #     _to_microseconds(start),
    #     _to_microseconds(end),
    #     categories=categories)

    # _frames.append(frame)

def profiled(*categories: str) -> t.Callable[[t.Callable[_AT, _RT]], t.Callable[_AT, _RT]]:
    '''
    A decorator function that enables profiling execution of given
    callable. It automatically logs execution time and saves it to profile
    file. This decorator is only applied when running in debug mode.

    @categories: A profile categories with which profile result will be associated.
    '''

    assert len(categories) > 0, 'Profiling categories list cannot be empty'

    def outer(func: t.Callable[_AT, _RT]) -> t.Callable[_AT, _RT]:
        @functools.wraps(func)
        def inner(*args: _AT.args, **kwargs: _AT.kwargs) -> _RT:
            _logger = logging.getLogger(__name__)

            start = time.perf_counter()
            res = func(*args, **kwargs)
            end = time.perf_counter()

            profile(func, start, end, categories)

            return res

        if __debug__:
            return inner

        return func

    return outer

def _close_profiler() -> None:
    _dump_frames(_frames.copy())

    with _write_lock:
        _file.write(_FOOTER)
        _file.close()

@profiled('debugging')
def _dump_frames(frames: list[_ProfileFrame]) -> None:
    global _buffer

    with _write_lock:
        for frame in frames:
            frame.dump(_buffer)

        _file.write(_buffer.getvalue())
        _file.flush()
        _buffer = io.StringIO()

def _to_microseconds(time_ns: int) -> float:
    return time_ns / (10 ** 3)

_frames: list[str] = []
_file = open(paths.PROFILE_FILE, 'w+')
_write_lock = threading.RLock()
_buffer = io.StringIO()
