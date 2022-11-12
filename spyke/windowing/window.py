import logging

import glfw
from PIL import Image

from spyke import debug, events, paths
from spyke.enums import Key
from spyke.exceptions import GraphicsException
from spyke.runtime import DisposableBase
from spyke.windowing import WindowSpecs, glfw_callbacks

_OPENGL_REQUIRED_VERSION = (4, 5)

class Window(DisposableBase):
    @debug.profiled('graphics', 'initialization')
    def __init__(self, specification: WindowSpecs):
        super().__init__()

        self._is_active = True
        self._is_vsync_on = True

        if not glfw.init():
            raise GraphicsException('Cannot initialize GLFW.')

        _set_default_window_flags(specification)

        if specification.fullscreen:
            self._handle = _create_window_fullscreen(specification)
        else:
            self._handle = _create_window_normal(specification)

        self._size = glfw.get_framebuffer_size(self._handle)

        glfw.make_context_current(self._handle)

        input_mode = glfw.CURSOR_NORMAL if specification.cursor_visible else glfw.CURSOR_HIDDEN
        glfw.set_input_mode(self._handle, glfw.CURSOR, input_mode)

        icon_filepath = specification.icon_filepath or paths.DEFAULT_ICON_FILEPATH
        with Image.open(icon_filepath) as img:
            glfw.set_window_icon(self._handle, 1, img)

        glfw_callbacks.register(self._handle)
        events.register(self._change_focus_callback, events.WindowChangeFocusEvent, priority=-1)
        events.register(self._resize_callback, events.ResizeEvent, priority=-1)

        self.set_vsync(specification.vsync)

        _logger.info('Window created.')

    def set_title(self, title: str) -> None:
        glfw.set_window_title(self._handle, title)

    def set_vsync(self, value: bool) -> None:
        glfw.swap_interval(int(value))
        self._is_vsync_on = value
        _logger.debug('Vsync set to: %s.', value)

    @debug.profiled('graphics', 'window', 'rendering')
    def swap_buffers(self) -> None:
        glfw.swap_buffers(self._handle)

    @debug.profiled('graphics', 'window', 'events')
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

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @debug.profiled('window')
    def _dispose(self) -> None:
        glfw.destroy_window(self._handle)
        _logger.debug('Window destroyed.')

        glfw.terminate()
        _logger.debug('Glfw terminated.')

    def _change_focus_callback(self, event: events.WindowChangeFocusEvent) -> None:
        self._is_active = event.value

    def _key_down_callback(self, event: events.KeyDownEvent) -> None:
        if event.repeat:
            return

        if event.key == Key.F2:
            self.set_vsync(not self._is_vsync_on)

    def _resize_callback(self, e: events.ResizeEvent) -> None:
        self._size = e.size

@debug.profiled('window')
def _create_window_normal(specification: WindowSpecs) -> glfw._GLFWwindow:
    glfw.window_hint(glfw.RESIZABLE, specification.resizable)
    glfw.window_hint(glfw.DECORATED, not specification.borderless)

    return glfw.create_window(
        specification.width,
        specification.height,
        specification.title,
        None,
        None)

@debug.profiled('window')
def _create_window_fullscreen(specification: WindowSpecs) -> glfw._GLFWwindow:
    mon = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(mon)

    glfw.window_hint(glfw.RED_BITS, mode.bits.red)
    glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
    glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
    glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

    _logger.info('Creating window using fullscreen mode at monitor "%s".', glfw.get_monitor_name(mon).decode('ansi'))

    return glfw.create_window(
        mode.size.width,
        mode.size.height,
        specification.title,
        mon,
        None)

def _set_default_window_flags(specification: WindowSpecs) -> None:
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

_logger = logging.getLogger(__name__)
