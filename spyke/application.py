import abc
import time

import psutil

from spyke import debug, events, resources
from spyke.audio import AudioDevice
from spyke.debug import profiling
from spyke.graphics import renderer, window

__all__ = ['Application']

class Application(abc.ABC):
    @debug.profiled('application', 'initialization')
    def __init__(self, window_specification: window.WindowSpec, use_imgui: bool=False):
        self._is_running = False
        self._frametime = 1.0
        self._window_spec = window_specification

        self._audio_device = AudioDevice()
        self._process = psutil.Process()

        # TODO: Reimplement imgui
        # if use_imgui:
            # self._imgui = Imgui()


        # TODO: Implement this at some point
        # enginePreview.RenderPreview()
        # glfw.swap_buffers(self._handle)

    def on_frame(self, frametime: float) -> None:
        pass

    def on_close(self) -> None:
        pass

    def on_load(self) -> None:
        pass

    @property
    def frametime(self) -> float:
        return self._frametime

    @property
    def audio_device(self) -> AudioDevice:
        return self._audio_device

    @debug.profiled('application', 'initialization')
    def _load(self) -> None:
        window.initialize(self._window_spec)
        resources.initialize()
        renderer.initialize(window.get_width(), window.get_height())

        self.on_load()

    @debug.profiled('application')
    def _process_frame(self) -> None:
        start = time.perf_counter()

        window.process_events()
        events.process_events()
        resources.process_loading_queue()

        if window.is_active():
            window.swap_buffers()
            renderer.clear()

            self.on_frame(self._frametime)

        self._frametime = time.perf_counter() - start

        self._update_counters()

    def run(self) -> None:
        self._load()

        while not window.should_close():
            self._process_frame()

        self._close()

    def _close(self) -> None:
        self.on_close()

        resources.unload_all()
        renderer.shutdown()
        window.shutdown()
        self._audio_device.dispose()

        profiling._close_profiler()

    def _update_counters(self) -> None:
        if not __debug__:
            return

        memory = self._process.memory_info().rss / 1_000_000

        profiling.update_counter('memory (MB)', memory)
        profiling.update_counter('frametime (ms)', self._frametime * 1000)
