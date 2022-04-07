from __future__ import annotations
from spyke.windowing.windowSpecs import WindowSpecs
from spyke.windowing.window import Window
from spyke.graphics.rendering import Renderer
from spyke.audio import AudioDevice
from spyke.ecs import scene
from spyke import events, utils, resources
from abc import ABC, abstractmethod
import atexit
import time
import logging

__all__ = [
    'Application',
]

_LOGGER = logging.getLogger(__name__)

class Application(ABC):
    def __init__(self, window_specification: WindowSpecs):
        self._loading_start: float = time.perf_counter()

        self._window: Window = Window(window_specification)
        self._renderer: Renderer = Renderer()
        self._audio_device: AudioDevice = AudioDevice()

        # TODO: Implement this at some point
        # enginePreview.RenderPreview()
        # glfw.swap_buffers(self._handle)

    @abstractmethod
    def on_frame(self) -> None:
        pass

    @abstractmethod
    def on_close(self) -> None:
        pass

    @abstractmethod
    def on_load(self) -> None:
        pass

    def _close(self) -> None:
        scene.cleanup()
        resources.unload_all()
        self._renderer.shutdown()
        self._window.close()
        self._audio_device.close()

        _LOGGER.info('Application closed.')

    def _run(self) -> None:
        events.register(lambda e: self.window.set_vsync(e.state), events.ToggleVsyncEvent, priority=-1)
        atexit.register(self._close)

        self.renderer.initialize(self.window.handle)
        self.on_load()
        utils.garbage_collect()
        
        _LOGGER.info('Application loaded in %f seconds.', time.perf_counter() - self._loading_start)

        # enginePreview.CleanupPreview()
        # glfw.swap_buffers(self._handle)

        is_running = True
        while is_running:
            start = self.window.get_time()

            if self.window.should_close:
                events.invoke(events.WindowCloseEvent())
                is_running = False
            
            events._process_events()

            _scene = scene.get_current()
            _scene.process(dt=self.frametime)

            if self.renderer.info.window_active:
                self.renderer.render_scene(_scene)
                self.on_frame()
                self.window.swap_buffers()

            self.window.process_events()

            self.renderer.info.frametime = self.window.get_time() - start

        self.on_close()
        self._close()
        atexit.unregister(self._close)

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
