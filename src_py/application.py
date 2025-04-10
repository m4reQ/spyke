import abc
import enum
import time

import psutil

from spyke import assets, debug, scheduler
from spyke.debug import profiling
from spyke.graphics import renderer, shader_cache, window


class Application(abc.ABC):
    def __init__(self,
                 window_settings: window.WindowSettings,
                 target_fps: float | None = None,
                 timing_policy: scheduler.SchedulerPolicy = scheduler.SchedulerPolicy.RELAXED):
        self._is_running = False
        self._frametime = 1.0
        self._scheduler = scheduler.Scheduler(
            float('inf') if target_fps is None else 1.0 / target_fps,
            timing_policy)
        self._window_settings = window_settings
        self._process = psutil.Process()

    def on_update(self, frametime: float) -> None:
        pass

    def on_render(self, frametime: float) -> None:
        pass

    def on_close(self) -> None:
        pass

    def on_load(self) -> None:
        pass

    @property
    def frametime(self) -> float:
        return self._frametime

    @debug.profiled
    def _load(self) -> None:
        shader_cache.set(shader_cache.ShaderCache('./shadercache'))

        with debug.profiled_scope('intialize_window'):
            window.initialize(self._window_settings)

        renderer.initialize(window.get_width(), window.get_height())

        self.on_load()

    @debug.profiled
    def _process_frame(self) -> None:
        # render
        if window.is_visible():
            self._scheduler.schedule_main_thread_priority_job(self.on_render, 0, self._frametime)
            self._scheduler.schedule_main_thread_priority_job(_swap_buffers, 0)

        # update
        self._scheduler.schedule_main_thread_priority_job(_process_window_events, 0)
        self._scheduler.schedule_main_thread_priority_job(self.on_update, 0, self._frametime)

        assets.schedule_loading_tasks(self._scheduler, priority=2)
        renderer.schedule_texture_uploads(self._scheduler, priority=1)

        self._frametime = self._scheduler.dispatch_jobs()
        self._update_counters()

    def run(self) -> None:
        debug.begin_profiling_session('./spyke_profile.json')
        self._load()

        while not window.should_close():
            self._process_frame()

        self._close()
        profiling.end_profiling_session()

    def _close(self) -> None:
        self.on_close()

        assets.unload_all()
        renderer.shutdown()
        window.shutdown()

    def _update_counters(self) -> None:
        if not __debug__:
            return

        memory = self._process.memory_info().rss / 1_000_000

        profiling.update_profiling_counter(memory, 'memory (MB)')
        profiling.update_profiling_counter(self._frametime * 1000, 'frametime (ms)')

@debug.profiled
def _swap_buffers() -> None:
    window.swap_buffers()

@debug.profiled
def _process_window_events() -> None:
    window.process_events()
