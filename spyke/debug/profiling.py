import threading
import typing as t
import dataclasses
import time
import json
import os

from spyke import paths

def _to_microseconds(time_ns: int) -> float:
    return time_ns / (10 ** 3)

@dataclasses.dataclass
class _ProfileFrame:
    name: str
    time_start: float
    time_end: float
    thread_id: int = dataclasses.field(default_factory=threading.get_ident)
    process_id: int = dataclasses.field(default_factory=os.getpid)
    categories: t.Iterable[str] = dataclasses.field(default_factory=list)
            
    def to_chrome_events(self) -> list[dict[str, t.Any]]:
        return [{
            'name': self.name,
            'cat': ','.join(self.categories),
            'ph': 'B',
            'ts': self.time_start,
            'tid': self.thread_id,
            'pid': self.process_id},
            {
            'name': self.name,
            'cat': ','.join(self.categories),
            'ph': 'E',
            'ts': self.time_end,
            'tid': self.thread_id,
            'pid': self.process_id}]
    
class ChromeProfiler:
    '''
    A profiler that saves informations about execution time
    and memory consumption in Chrome Traceback format, which can
    be later inspected using Chrome Trace viewer.
    '''
    
    def __init__(self, filepath: str):
        self.file = open(filepath, 'w+', encoding='utf-8')
        self.start_time = time.perf_counter_ns()
        self.lock = threading.Lock()
        
        self.frames: list[_ProfileFrame] = []
    
    def add_profile(self,
                    func: t.Callable,
                    start: int,
                    end: int,
                    categories: t.Iterable[str]) -> None:
        frame = _ProfileFrame(
            func.__qualname__,
            _to_microseconds(start),
            _to_microseconds(end),
            categories=categories)
        
        self.frames.append(frame)
    
    def save_profile(self, filepath: str) -> None:
        events: list[dict[str, t.Any]] = []
        for frame in self.frames:
            events.extend(frame.to_chrome_events())
            
        with open(filepath, 'w+', encoding='utf-8') as f:
            f.write('{"traceEvents":[')
            
            for idx, event in enumerate(events):
                json.dump(event, f)
                if idx + 1 != len(events):
                    f.write(',')
            
            f.write(']}')

_profiler: t.Optional[ChromeProfiler] = None

def get_profiler() -> ChromeProfiler:
    global _profiler
    
    if _profiler is None:
        _profiler = ChromeProfiler(paths.PROFILE_FILE)
    
    return _profiler