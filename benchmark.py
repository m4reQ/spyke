import random
import tracemalloc
import linecache
from typing import Callable, Sequence
import logging
import gc
import sys
import timeit
import dataclasses

TIMING_EXECUTIONS_COUNT = 1000
TIMING_TESTS_REPEATS = 5


@dataclasses.dataclass
class _BenchmarkResult:
    snapshot: tracemalloc.Snapshot
    gc_size_0: int
    gc_size_1: int
    execution_time: float
    executions_count: int
    function_name: str


def _display(result: _BenchmarkResult):
    filters = (
        tracemalloc.Filter(True, __file__),
    )
    snapshot = result.snapshot.filter_traces(filters)
    stats = snapshot.statistics('traceback')

    title = f'Results for {result.function_name}'
    print('\n' + title)
    print('-' * len(title))

    size = sum(stat.size for stat in stats)
    print(f'Total allocated: {size / 1000:.3f} kb')

    peak = stats[0]
    frame = peak.traceback[0]
    line = linecache.getline(frame.filename, frame.lineno).strip()
    print(
        f'Highest allocation-heavy call allocates (average for {peak.count} call{"s" if peak.count > 1 else ""}): {int(peak.size / peak.count)} b')
    print('Highest allocation-heavy line:')
    if line:
        print(f'\t"{line}"')

    print('GC object size difference:')
    print(f'\tGeneration 0: {result.gc_size_0} b')
    print(f'\tGeneration 1: {result.gc_size_1} b')

    time = int((result.execution_time /
               result.executions_count) * (10 ** 6))

    print(
        f'Average execution time ({result.executions_count} executions): {time} microseconds')


def _get_gc_size(generation: int) -> int:
    return sum(sys.getsizeof(obj) for obj in gc.get_objects(generation))


def _run(func: Callable):
    logging.debug('Running cleanup before test...')
    if tracemalloc.is_tracing():
        tracemalloc.stop()

    tracemalloc.clear_traces()
    gc.collect()

    logging.debug('Running allocations benchmark...')
    tracemalloc.start()

    func()

    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()

    logging.debug('Running gc benchmark...')
    gc.collect()
    gen0_size = _get_gc_size(0)
    gen1_size = _get_gc_size(1)

    _ = func()

    gen0_diff = _get_gc_size(0) - gen0_size
    gen1_diff = _get_gc_size(1) - gen1_size

    logging.debug('Running execution time profiling.')

    results = timeit.repeat(f'{func.__name__}()',
                            globals=globals(), number=TIMING_EXECUTIONS_COUNT, repeat=TIMING_TESTS_REPEATS)

    result = _BenchmarkResult(snapshot, gen0_diff, gen1_diff, sum(
        results) / TIMING_TESTS_REPEATS, TIMING_EXECUTIONS_COUNT, func.__name__)
    _display(result)


def run(tests: Sequence[Callable]):
    for test in tests:
        _run(test)


def test1():
    l = (random.randint(0, i) for i in range(100))
    s = (str(x) for x in l)

    return zip(l, s)


def test2():
    l = list(random.randint(0, i) for i in range(100))
    s = list(str(x) for x in l)

    return list(zip(l, s))


def test3():
    l = []
    for i in range(100):
        x = random.randint(0, i)
        l.append(x)

    s = []
    for x in l:
        s.append(str(x))

    z = []
    for i in range(100):
        z.append((l[i], s[i]))

    return z


if __name__ == '__main__':
    run((test1, test2, test3))
