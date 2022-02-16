from __future__ import annotations

from spyke.exceptions import GraphicsException
from spyke.windowing import WindowSpecs
from spyke.windowing import glfwCallbacks
# TODO: Do something with those constants AAAAAAAAAAAAAA
from spyke.constants import DEFAULT_ICON_FILEPATH
from spyke.utils import Deletable
from spyke import debug
import glfw
from PIL import Image

_OPENGL_REQUIRED_VERSION = (4, 5)


class Window(Deletable):
    # TODO: Decide if we want to move whole window creation to
    # separate initalize method or if we should leave it in constructor
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

        icon_filepath = specification.icon_filepath or DEFAULT_ICON_FILEPATH
        with Image.open(icon_filepath) as img:
            glfw.set_window_icon(self._handle, 1, img)

        glfwCallbacks.register(self._handle)

    def set_title(self, title: str) -> None:
        glfw.set_window_title(self._handle, title)

    def set_vsync(self, value: bool) -> None:
        glfw.swap_interval(int(value))
        debug.log_info(f'Vsync set to: {value}.')

    def swap_buffers(self) -> None:
        glfw.swap_buffers(self._handle)

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
    
    def _delete(self) -> None:
        glfw.destroy_window(self._handle)
        debug.log_info('Window destroyed.')

        glfw.terminate()
        debug.log_info('Glfw terminated.')

    def _create_window_normal(self, specification: WindowSpecs) -> None:
        glfw.window_hint(glfw.RESIZABLE, specification.resizable)
        glfw.window_hint(glfw.DECORATED, not specification.borderless)

        self._handle = glfw.create_window(
            specification.width, specification.height, specification.title, None, None)

    def _create_window_fullscreen(self, specification: WindowSpecs) -> None:
        mon = glfw.get_primary_monitor()
        mode = glfw.get_video_mode(mon)

        glfw.window_hint(glfw.RED_BITS, mode.bits.red)
        glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
        glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
        glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

        self._handle = glfw.create_window(
            specification.width, specification.height, specification.title, mon, None)

    def _set_default_window_flags(self, specification: WindowSpecs) -> None:
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,
                         _OPENGL_REQUIRED_VERSION[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,
                         _OPENGL_REQUIRED_VERSION[1])
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SAMPLES, specification.samples)
