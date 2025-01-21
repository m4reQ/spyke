import abc
import time

import psutil

from spyke import assets, debug
from spyke.debug import profiling
from spyke.graphics import renderer, window


class Application(abc.ABC):
    @debug.profiled('application', 'initialization')
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

    @debug.profiled('application', 'initialization')
    def _load(self) -> None:
        window.initialize(self._window_settings)
        renderer.initialize(window.get_width(), window.get_height())

        self.on_load()

    @debug.profiled('application')
    def _process_frame(self) -> None:
        start = time.perf_counter()

        window.process_events()
        assets.process_loading_queue()

        self.on_update(self._frametime)

        if window.is_visible():
            self.on_render(self._frametime)
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

        profiling._close_profiler()

    def _update_counters(self) -> None:
        if not __debug__:
            return

        memory = self._process.memory_info().rss / 1_000_000

        profiling.update_counter('memory (MB)', memory)
        profiling.update_counter('frametime (ms)', self._frametime * 1000)
