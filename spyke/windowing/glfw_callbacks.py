import logging

import glfw
from spyke import events
from spyke.exceptions import GraphicsException

_logger = logging.getLogger(__name__)

def register(window: glfw._GLFWwindow):
    glfw.set_error_callback(_error_callback)

    glfw.set_framebuffer_size_callback(window, _resize_cb)
    glfw.set_cursor_pos_callback(window, _cursor_pos_callback)
    glfw.set_window_iconify_callback(window, _iconify_callback)
    glfw.set_mouse_button_callback(window, _mouse_callback)
    glfw.set_scroll_callback(window, _mouse_scroll_callback)
    glfw.set_key_callback(window, _key_callback)
    glfw.set_window_pos_callback(window, _window_pos_callback)
    glfw.set_window_focus_callback(window, _window_focus_callback)
    glfw.set_window_close_callback(window, _window_close_callback)

    _logger.debug('GLFW window callbacks registered.')

def _error_callback(code: int, message: str) -> None:
    raise GraphicsException(f'GLFW error: {message} ({code}).')

def _resize_cb(_, width: int, height: int) -> None:
    events.invoke(events.ResizeEvent(width, height))
    _logger.info('Window resized to (%d, %d)', width, height)

def _window_close_callback(_) -> None:
    events.invoke(events.WindowCloseEvent())

def _window_focus_callback(_, value: int) -> None:
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
