import logging

import glfw
from PIL import Image

from spyke import paths, debug
from spyke.exceptions import GraphicsException
from spyke.windowing import WindowSpecs
from spyke.windowing import glfw_callbacks

_OPENGL_REQUIRED_VERSION = (4, 5)
_logger = logging.getLogger(__name__)

class Window:
    @debug.profiled('graphics', 'initialization')
    def __init__(self, specification: WindowSpecs):
        super().__init__()

        self._handle: glfw._GLFWwindow

        if not glfw.init():
            raise GraphicsException('Cannot initialize GLFW.')

        self._set_default_window_flags(specification)

        if specification.fullscreen:
            self._create_window_fullscreen(specification)
        else:
            self._create_window_normal(specification)

        glfw.make_context_current(self._handle)

        input_mode = glfw.CURSOR_NORMAL if specification.cursor_visible else glfw.CURSOR_HIDDEN
        glfw.set_input_mode(self._handle, glfw.CURSOR, input_mode)

        icon_filepath = specification.icon_filepath or paths.DEFAULT_ICON_FILEPATH
        with Image.open(icon_filepath) as img:
            glfw.set_window_icon(self._handle, 1, img)

        glfw_callbacks.register(self._handle)

        self.set_vsync(specification.vsync)

        _logger.info('Window created.')

    def set_title(self, title: str) -> None:
        glfw.set_window_title(self._handle, title)

    def set_vsync(self, value: bool) -> None:
        glfw.swap_interval(int(value))
        _logger.debug('Vsync set to: %s.', value)

    def swap_buffers(self) -> None:
        glfw.swap_buffers(self._handle)

    @debug.profiled('graphics', 'window')
    def process_events(self) -> None:
        glfw.poll_events()

    def get_time(self) -> float:
        return glfw.get_time()

    @property
    def handle(self) -> glfw._GLFWwindow:
        return self._handle

    @property
    def should_close(self) -> bool:
        return glfw.window_should_close(self._handle)

    def close(self) -> None:
        glfw.destroy_window(self._handle)
        _logger.debug('Window destroyed.')

        glfw.terminate()
        _logger.debug('Glfw terminated.')

    def _create_window_normal(self, specification: WindowSpecs) -> None:
        glfw.window_hint(glfw.RESIZABLE, specification.resizable)
        glfw.window_hint(glfw.DECORATED, not specification.borderless)

        self._handle = glfw.create_window(
            specification.width,
            specification.height,
            specification.title,
            None,
            None)

    def _create_window_fullscreen(self, specification: WindowSpecs) -> None:
        mon = glfw.get_primary_monitor()
        mode = glfw.get_video_mode(mon)

        glfw.window_hint(glfw.RED_BITS, mode.bits.red)
        glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
        glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
        glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

        self._handle = glfw.create_window(
            specification.width,
            specification.height,
            specification.title,
            mon,
            None)

    def _set_default_window_flags(self, specification: WindowSpecs) -> None:
        glfw.window_hint(
            glfw.CONTEXT_VERSION_MAJOR,
            _OPENGL_REQUIRED_VERSION[0])
        glfw.window_hint(
            glfw.CONTEXT_VERSION_MINOR,
            _OPENGL_REQUIRED_VERSION[1])
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SAMPLES, specification.samples)
        glfw.window_hint(glfw.OPENGL_DEBUG_CONTEXT, __debug__)
