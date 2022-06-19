import abc
import atexit
import time
import logging

from spyke import events, utils, resources, debug, paths
from spyke.resources import loading_queue
from spyke.audio import AudioDevice
from spyke.ecs import scene
from spyke.windowing.window_specs import WindowSpecs
from spyke.windowing.window import Window
from spyke.graphics.rendering import Renderer

__all__ = [
    'Application',
]

_logger = logging.getLogger(__name__)

class Application(abc.ABC):
    def __init__(self, window_specification: WindowSpecs):
        self._loading_start: float = time.perf_counter()

        self._window: Window = Window(window_specification)
        self._renderer: Renderer = Renderer()
        self._audio_device: AudioDevice = AudioDevice()

        # TODO: Implement this at some point
        # enginePreview.RenderPreview()
        # glfw.swap_buffers(self._handle)

    @abc.abstractmethod
    def on_frame(self) -> None:
        pass

    @abc.abstractmethod
    def on_close(self) -> None:
        pass

    @abc.abstractmethod
    def on_load(self) -> None:
        pass

    def _close(self) -> None:
        atexit.unregister(self._close)
        
        profiler = debug.get_profiler()
        profiler.save_profile(paths.PROFILE_FILE)
        
        resources.unload_all()
        self._renderer.shutdown()
        self._window.close()
        self._audio_device.close()
        
        _logger.info('Application closed.')

    def _run(self) -> None:
        events.register(lambda e: self._window.set_vsync(e.state), events.ToggleVsyncEvent, priority=-1)
        atexit.register(self._close)

        self._renderer.initialize(self._window.handle)
        self.on_load()
        utils.garbage_collect()

        _logger.info('Application loaded in %f seconds.', time.perf_counter() - self._loading_start)

        # enginePreview.CleanupPreview()
        # glfw.swap_buffers(self._handle)

        is_running = True
        while is_running:
            start = self._window.get_time()

            if self._window.should_close:
                events.invoke(events.WindowCloseEvent())
                is_running = False

            events.process_events()
            loading_queue.process_loading_queue()

            _scene = scene.get_current()
            _scene.process(dt=self.frametime)

            if self._renderer.info.window_active:
                self._renderer.render_scene(_scene)
                self.on_frame()
                self._window.swap_buffers()

            self._window.process_events()

            self._renderer.info.frametime = self._window.get_time() - start

        self.on_close()
        self._close()

    @property
    def frametime(self) -> float:
        return self._renderer.info.frametime

    @property
    def renderer(self) -> Renderer:
        return self._renderer

    @property
    def window(self) -> Window:
        return self._window

    @property
    def audio_device(self) -> AudioDevice:
        return self._audio_device
