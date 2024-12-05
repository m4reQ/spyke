import dataclasses
import logging

import glfw
from PIL import Image

from spyke import debug, events, paths


@dataclasses.dataclass
class WindowSpec:
    '''
    A structure used to configure window.
    '''

    width: int
    height: int
    title: str
    samples: int = 1
    vsync: bool = True
    resizable: bool = True
    fullscreen: bool = False
    borderless: bool = False
    cursor_visible: bool = True
    icon_filepath: str | None = None

@debug.profiled('window', 'initialization')
def initialize(spec: WindowSpec) -> None:
    global _handle, _width, _height

    _initialize_glfw()
    _set_default_window_flags(spec.samples)

    if spec.fullscreen:
        _handle = _create_window_fullscreen(spec)
    else:
        _handle = _create_window_normal(spec)

    _width, _height = glfw.get_framebuffer_size(_handle)

    glfw.make_context_current(_handle)
    glfw.set_input_mode(
        _handle,
        glfw.CURSOR,
        glfw.CURSOR_NORMAL if spec.cursor_visible else glfw.CURSOR_HIDDEN)

    _set_window_icon(spec.icon_filepath or paths.DEFAULT_ICON_FILEPATH)
    _register_window_callbacks()

    set_vsync(spec.vsync)

def shutdown() -> None:
    glfw.destroy_window(_handle)
    _logger.debug('Window destroyed.')

    glfw.terminate()
    _logger.debug('Glfw terminated.')

def get_width() -> int:
    return _width

def get_height() -> int:
    return _height

def is_active() -> bool:
    return _is_active

def should_close() -> bool:
    return _should_close

def set_title(title: str) -> None:
    glfw.set_window_title(_handle, title)

def set_vsync(value: bool) -> None:
    glfw.swap_interval(int(value))

@debug.profiled('window')
def resize(width: int, height: int) -> None:
    glfw.set_window_size(_handle, width, height)

@debug.profiled('window')
def swap_buffers() -> None:
    glfw.swap_buffers(_handle)

@debug.profiled('window')
def process_events() -> None:
    glfw.poll_events()

@debug.profiled('window', 'initialization')
def _set_window_icon(filepath: str) -> None:
    with Image.open(filepath) as img:
        glfw.set_window_icon(_handle, 1, img)

@debug.profiled('window', 'initialization')
def _create_window_normal(specification: WindowSpec) -> glfw._GLFWwindow:
    glfw.window_hint(glfw.RESIZABLE, specification.resizable)
    glfw.window_hint(glfw.DECORATED, not specification.borderless)

    return glfw.create_window(
        specification.width,
        specification.height,
        specification.title,
        None,
        None)

@debug.profiled('window', 'initialization')
def _create_window_fullscreen(specification: WindowSpec) -> glfw._GLFWwindow:
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

@debug.profiled('window', 'initialization')
def _set_default_window_flags(samples: int) -> None:
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 5)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.SAMPLES, samples)
    glfw.window_hint(glfw.OPENGL_DEBUG_CONTEXT, __debug__)

@debug.profiled('window', 'initialization')
def _initialize_glfw() -> None:
    if not glfw.init():
        raise RuntimeError(f'Failed to initialize GLFW: {_get_glfw_error()}')

def _get_glfw_error() -> str:
    return glfw.get_error()[1]

@debug.profiled('window', 'initialization')
def _register_window_callbacks():
    glfw.set_error_callback(_error_callback)

    glfw.set_framebuffer_size_callback(_handle, _resize_cb)
    glfw.set_cursor_pos_callback(_handle, _cursor_pos_callback)
    glfw.set_window_iconify_callback(_handle, _iconify_callback)
    glfw.set_mouse_button_callback(_handle, _mouse_callback)
    glfw.set_scroll_callback(_handle, _mouse_scroll_callback)
    glfw.set_key_callback(_handle, _key_callback)
    glfw.set_window_pos_callback(_handle, _window_pos_callback)
    glfw.set_window_focus_callback(_handle, _window_focus_callback)
    glfw.set_window_close_callback(_handle, _window_close_callback)

    _logger.debug('GLFW window callbacks registered.')

def _error_callback(code: int, message: str) -> None:
    raise RuntimeError(f'GLFW error: {message} ({code}).')

def _resize_cb(_, width: int, height: int) -> None:
    global _width, _height

    _width = width
    _height = height

    events.invoke(events.ResizeEvent(width, height))

    _logger.info('Window resized to (%d, %d)', width, height)

def _window_close_callback(_) -> None:
    global _should_close
    _should_close = True

    events.invoke(events.WindowCloseEvent())

def _window_focus_callback(_, value: int) -> None:
    global _is_active
    _is_active = bool(value)

    events.invoke(events.WindowChangeFocusEvent(bool(value)))

def _cursor_pos_callback(_, x: int, y: int) -> None:
    events.invoke(events.MouseMoveEvent(x, y))

def _window_pos_callback(_, x: int, y: int) -> None:
    events.invoke(events.WindowMoveEvent(x, y))

def _iconify_callback(_, value: int) -> None:
    events.invoke(events.WindowChangeFocusEvent(bool(value)))

def _mouse_callback(_, button: int, action: int, mods: int) -> None:
    if action == glfw.PRESS:
        events.invoke(events.MouseButtonDownEvent(button, mods))
    elif action == glfw.RELEASE:
        events.invoke(events.MouseButtonUpEvent(button, mods))

def _mouse_scroll_callback(_, x_offset: float, y_offset: float) -> None:
    events.invoke(events.MouseScrollEvent(x_offset, y_offset))

def _key_callback(_, key, scancode: int, action: int, mods: int) -> None:
    if action == glfw.PRESS:
        events.invoke(events.KeyDownEvent(key, mods, scancode, False))
    elif action == glfw.REPEAT:
        events.invoke(events.KeyDownEvent(key, mods, scancode, True))
    elif action == glfw.RELEASE:
        events.invoke(events.KeyUpEvent(key))

_width = 0
_height = 0
_is_active = True
_should_close = False
_handle = glfw._GLFWwindow()
_logger = logging.getLogger(__name__)
