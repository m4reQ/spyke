import dataclasses
import atexit
import functools
import os
import threading
import time
import typing as t

from spyke import paths

_MAX_FRAMES = 400
_HEADER = '{"traceEvents":[{}'
_FOOTER = ']}'
_RT = t.TypeVar('_RT')
_AT = t.ParamSpec('_AT')
_FRAME_FORMAT = ',{{"name":"{}","cat":"{}","ph":"X","ts": {},"dur":{},"tid":{},"pid":{}}}'
_COUNTER_FORMAT = ',{{"name":"{}","ph":"C","ts":{},"pid":{},"args":{{"":{}}}}}'

@dataclasses.dataclass
class _ProfileFrame:
    name: str
    time_start: float
    time_end: float
    thread_id: int
    process_id: int
    categories: tuple[str, ...]

    def dump(self, file: t.TextIO) -> None:
        file.write(_FRAME_FORMAT.format(self.name, ','.join(self.categories), self.time_start - _profiler_time_start, self.time_end - self.time_start, self.thread_id, self.process_id))

class _ScopedProfiler:
    def __init__(self, name: str) -> None:
        self._name = name
        self._start = 0

    def __enter__(self) -> t.Self:
        self._start = time.perf_counter_ns()
        return self

    def __exit__(self, *_) -> None:
        profile(self._name, self._start, time.perf_counter_ns(), ('unknown',))

def initialize() -> None:
    with _write_lock:
        _file.write(_HEADER)
        _file.flush()

    atexit.register(_close_profiler)

def profile(name: str,
            start: int,
            end: int,
            categories: tuple[str, ...]) -> None:
    _ProfileFrame(
        name,
        _to_microseconds(start),
        _to_microseconds(end),
        threading.get_ident(),
        os.getpid(),
        categories).dump(_file)

def update_counter(name: str, value: float) -> None:
    if not __debug__:
        return

    _file.write(_COUNTER_FORMAT.format(name, _to_microseconds(time.perf_counter_ns()) - _profiler_time_start, os.getpid(), value))

def profiled_scope(name: str) -> _ScopedProfiler:
    return _ScopedProfiler(name)

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
            start = time.perf_counter_ns()
            res = func(*args, **kwargs)
            end = time.perf_counter_ns()

            profile(f'{func.__module__}:{func.__qualname__}', start, end, categories)

            return res

        if __debug__:
            return inner

        return func

    return outer

def _close_profiler() -> None:
    with _write_lock:
        _file.write(_FOOTER)
        _file.close()

def _to_microseconds(time_ns: int) -> float:
    return time_ns / (10 ** 3)

_file = open(paths.PROFILE_FILE, 'w+')
_file.write(_HEADER)
_write_lock = threading.RLock()
_profiler_time_start = _to_microseconds(time.perf_counter_ns())
