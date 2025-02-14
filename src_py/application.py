import abc
import time

import psutil

from spyke import assets, debug
from spyke.debug import profiling
from spyke.graphics import renderer, window


class Application(abc.ABC):
    @debug.profiled
    def __init__(self, window_settings: window.WindowSettings):
        self._is_running = False
        self._frametime = 1.0
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
        with debug.profiled_scope('intialize_window'):
            window.initialize(self._window_settings)

        renderer.initialize(window.get_width(), window.get_height())

        self.on_load()

    @debug.profiled
    def _process_frame(self) -> None:
        start = time.perf_counter()

        with debug.profiled_scope('process_window_events'):
            window.process_events()

        assets.process_loading_queue()

        self.on_update(self._frametime)

        if window.is_visible():
            self.on_render(self._frametime)

            with debug.profiled_scope('swap_buffers'):
                window.swap_buffers()

        self._frametime = time.perf_counter() - start

        self._update_counters()

    def run(self) -> None:
        self._load()

        while not window.should_close():
            self._process_frame()

        self._close()

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
