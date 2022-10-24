import abc
import logging
import time

from spyke import debug, events, resources, utils
from spyke.audio import AudioDevice
from spyke.graphics import opengl_object, renderer
from spyke.windowing import Window, WindowSpecs

__all__ = ['Application']

class Application(abc.ABC):
    @debug.profiled('application', 'initialization')
    def __init__(self, window_specification: WindowSpecs, use_imgui: bool=False):
        self._loading_start = time.perf_counter()
        self._is_running = False
        self._frametime = 0.0

        self._window = Window(window_specification)
        self._audio_device = AudioDevice()

        events.register(self._window_close_callback, events.WindowCloseEvent, priority=-1)

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
    def window(self) -> Window:
        return self._window

    @property
    def audio_device(self) -> AudioDevice:
        return self._audio_device

    def run(self) -> None:
        self._is_running = True

        resources.initialize()
        renderer.initialize(self._window.size)
        self.on_load()
        utils.garbage_collect()

        _logger.info('Application loaded in %f seconds.', time.perf_counter() - self._loading_start)

        # enginePreview.CleanupPreview()
        # glfw.swap_buffers(self._handle)

        while self._is_running:
            start = self._window.get_time()

            resources.process_loading_queue()
            events.process_events()

            # TEMPORARY !!!!!!
            # _scene = scene.get_current()
            # _scene.process(dt=self.frametime)

            if self._window.is_active:
                renderer.clear()
                self.on_frame(self._frametime)
                self._window.swap_buffers()

                # self._renderer.render_scene(_scene)
                # self.on_frame()
                # self._window.swap_buffers()

            self._window.process_events()
            self._frametime = self._window.get_time() - start

        self.on_close()

        opengl_object.delete_all()
        resources.unload_all()
        self._audio_device.dispose()
        self._window.dispose()

    def _window_close_callback(self, _) -> None:
        self._is_running = False

_logger = logging.getLogger(__name__)
