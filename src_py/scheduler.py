import enum
import queue
import time
import typing as t
from concurrent import futures

from spyke import debug

TJobArgs = t.ParamSpec('TJobArgs')

class SchedulerPolicy(enum.Enum):
    STRICT = enum.auto()
    RELAXED = enum.auto()

class _SchedulerJob:
    def __init__(self,
                 priority: int,
                 callback: t.Callable[TJobArgs, t.Any],
                 *job_args: TJobArgs.args,
                 **job_kwargs: TJobArgs.kwargs) -> None:
        self.priority = priority
        self.callback = callback
        self.args = job_args
        self.kwargs = job_kwargs

    def run(self) -> None:
        self.callback(*self.args, **self.kwargs)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _SchedulerJob):
            return self.priority == other.priority

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, _SchedulerJob):
            return self.priority < other.priority

        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, _SchedulerJob):
            return self.priority > other.priority

        return NotImplemented

    def __le__(self, other: object) -> bool:
        return not self.__gt__(other)

    def __ge__(self, other: object) -> bool:
        return not self.__lt__(other)

class Scheduler:
    def __init__(self,
                 max_frame_time: float,
                 policy: SchedulerPolicy,
                 max_threads: int | None = None) -> None:
        self.max_frame_time = max_frame_time
        self.policy = policy

        self._main_thread_jobs = queue.PriorityQueue[_SchedulerJob]()
        self._main_thread_priority_jobs = queue.PriorityQueue[_SchedulerJob]()
        self._aux_thread_jobs = queue.PriorityQueue[_SchedulerJob]()
        self._aux_thread_executor = futures.ThreadPoolExecutor(max_workers=max_threads)

    def schedule_main_thread_priority_job(self, job: t.Callable[TJobArgs, t.Any], priority: int, *job_args: TJobArgs.args, **job_kwargs: TJobArgs.kwargs) -> None:
        self._main_thread_priority_jobs.put(_SchedulerJob(priority, job, *job_args, **job_kwargs))

    def schedule_main_thread_job(self, job: t.Callable[TJobArgs, t.Any], priority: int, *job_args: TJobArgs.args, **job_kwargs: TJobArgs.kwargs) -> None:
        self._main_thread_jobs.put(_SchedulerJob(priority, job, *job_args, **job_kwargs))

    def schedule_aux_thread_job(self, job: t.Callable[TJobArgs, t.Any], priority: int, *job_args: TJobArgs.args, **job_kwargs: TJobArgs.kwargs) -> None:
        self._aux_thread_jobs.put(_SchedulerJob(priority, job, *job_args, **job_kwargs))

    def dispatch_jobs(self) -> float:
        start = time.perf_counter()

        # dispatch jobs for other threads
        self._dispatch_aux_thread_jobs()

        # dispatch all jobs that must run in the current frame
        self._dispatch_priority_jobs()

        # depending on the used policy run non-priority main thread jobs
        if self.policy == SchedulerPolicy.STRICT and self._max_frame_time_exceeded(start):
            # do not run any non-priority jobs when using strict policy
            return _get_frametime(start)

        # relaxed scheduler policy runs at least one non-priority job
        self._dispatch_main_thread_jobs(start)

        return _get_frametime(start)

    @debug.profiled
    def _dispatch_aux_thread_jobs(self) -> None:
        while not self._aux_thread_jobs.empty():
            job = self._aux_thread_jobs.get()
            self._aux_thread_executor.submit(job.run)

    @debug.profiled
    def _dispatch_priority_jobs(self) -> None:
        while not self._main_thread_priority_jobs.empty():
            job = self._main_thread_priority_jobs.get()
            job.run()

    @debug.profiled
    def _dispatch_main_thread_jobs(self, start: float) -> None:
        while not self._main_thread_jobs.empty():
            job = self._main_thread_jobs.get()
            job.run()

            if self._max_frame_time_exceeded(start):
                break

    def _max_frame_time_exceeded(self, start: float) -> bool:
        return time.perf_counter() - start > self.max_frame_time

def _get_frametime(start: float) -> float:
    return time.perf_counter() - start
