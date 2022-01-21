from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.graphics.windowSpecs import WindowSpecs

# from . import enginePreview
from spyke.graphics.gl import GLObject
from spyke.graphics.rendering import Renderer
from spyke import debug
from spyke import resourceManager
from spyke import events
from spyke.exceptions import GraphicsException, SpykeException
from spyke.constants import _OPENGL_VER_MAJOR, _OPENGL_VER_MINOR, DEFAULT_ICON_FILEPATH

import glfw
import os
import gc
from PIL import Image
from abc import ABC, abstractmethod


class Application(ABC):
    @debug.timed
    def __init__(self, specification: WindowSpecs):
        self.specification: WindowSpecs = specification
        self._handle: glfw._GLFWwindow = None
        self._renderer: Renderer = None

        if not glfw.init():
            raise GraphicsException('Cannot initialize GLFW.')

        glfw.set_error_callback(self._glfw_error_callback)

        self._set_default_window_flags()

        if specification.fullscreen:
            self._create_window_fullscreen()
        else:
            self._create_window_normal()

        glfw.make_context_current(self._handle)

        # TODO: Implement this at some point
        # enginePreview.RenderPreview()
        # glfw.swap_buffers(self._handle)

        input_mode = glfw.CURSOR_NORMAL if specification.cursor_visible else glfw.CURSOR_HIDDEN
        glfw.set_input_mode(self._handle, glfw.CURSOR, input_mode)

        glfw.set_framebuffer_size_callback(self._handle, self._resize_cb)
        glfw.set_cursor_pos_callback(self._handle, self._cursor_pos_callback)
        glfw.set_window_iconify_callback(self._handle, self._iconify_callback)
        glfw.set_mouse_button_callback(self._handle, self._mouse_callback)
        glfw.set_scroll_callback(self._handle, self._mouse_scroll_callback)
        glfw.set_key_callback(self._handle, self._key_callback)
        glfw.set_window_pos_callback(self._handle, self._window_pos_callback)
        glfw.set_window_focus_callback(
            self._handle, self._window_focus_callback)

        events.register_method(lambda e: self.set_vsync(e.state),
                               events.ToggleVsyncEvent, priority=-1)

        # TODO: Move this to resource manager
        if specification.icon_filepath:
            if not os.path.endswith('.ico'):
                raise SpykeException(
                    f'Invalid icon extension: {os.path.splitext(specification.icon_filepath)}.')

            self._load_icon(specification.icon_filepath)
        else:
            self._load_icon(DEFAULT_ICON_FILEPATH)

        self._renderer = Renderer()
        self._renderer.initialize(self._handle)

        self.set_vsync(specification.vsync)

        gc.collect()

    @abstractmethod
    def on_frame(self) -> None:
        pass

    @abstractmethod
    def on_close(self) -> None:
        pass

    @abstractmethod
    def on_load(self) -> None:
        pass

    def set_title(self, title: str) -> None:
        glfw.set_window_title(self._handle, title)

    def set_vsync(self, value: bool) -> None:
        glfw.swap_interval(int(value))
        debug.log_info(f'Vsync set to: {value}.')

    def _run(self) -> None:
        # TODO: Add loading time profiling
        self.on_load()
        resourceManager.FinishLoading()

        # enginePreview.CleanupPreview()
        # glfw.swap_buffers(self._handle)

        isRunning = True
        while isRunning:
            start = glfw.get_time()

            if glfw.window_should_close(self._handle):
                events.invoke(events.WindowCloseEvent())
                isRunning = False

            scene = resourceManager.GetCurrentScene()
            scene.Process(dt=self.frametime)

            if self.renderer.info.window_active:
                self.renderer.render_scene(scene)
                self.on_frame()
                glfw.swap_buffers(self._handle)

            glfw.poll_events()

            self._renderer.info.frametime = glfw.get_time() - start

        self.on_close()
        self._close()

    def _glfw_error_callback(self, code: int, message: str) -> None:
        raise GraphicsException(f'GLFW error: {message} ({code}).')

    def _resize_cb(self, _, width, height) -> None:
        events.invoke(events.ResizeEvent(width, height))
        debug.log_info(f'Window resized to ({width}, {height})')

    def _window_focus_callback(self, _, value) -> None:
        event = events.WindowFocusEvent() if value else events.WindowLostFocusEvent()
        events.invoke(event)

    def _cursor_pos_callback(self, _, x, y) -> None:
        events.invoke(events.MouseMoveEvent(x, y))

    def _window_pos_callback(self, _, x, y) -> None:
        events.invoke(events.WindowMoveEvent(x, y))

    def _iconify_callback(self, _, value) -> None:
        events.invoke(events.WindowChangeFocusEvent(value))

    def _mouse_callback(self, _, button, action, mods) -> None:
        if action == glfw.PRESS:
            events.invoke(events.MouseButtonDownEvent(button, mods))
        elif action == glfw.RELEASE:
            events.invoke(events.MouseButtonUpEvent(button, mods))

    def _mouse_scroll_callback(self, _, xOffset, yOffset) -> None:
        events.invoke(events.MouseScrollEvent(xOffset, yOffset))

    def _key_callback(self, _, key, scancode, action, mods) -> None:
        if action == glfw.PRESS:
            events.invoke(events.KeyDownEvent(key, mods, scancode, False))
        elif action == glfw.REPEAT:
            events.invoke(events.KeyDownEvent(key, mods, scancode, True))
        elif action == glfw.RELEASE:
            events.invoke(events.KeyUpEvent(key))

    # TODO: Move this somewhere else. Maybe to resource manager
    def _load_icon(self, filepath: str) -> None:
        img = Image.open(filepath)
        glfw.set_window_icon(self._handle, 1, img)
        img.close()

    @debug.timed
    def _close(self) -> None:
        GLObject.delete_all()

        glfw.destroy_window(self._handle)
        debug.log_info('Window destroyed.')

        glfw.terminate()
        debug.log_info('Glfw terminated.')

    def _create_window_normal(self) -> None:
        glfw.window_hint(glfw.RESIZABLE, self.specification.resizable)
        glfw.window_hint(glfw.DECORATED, not self.specification.borderless)

        self._handle = glfw.create_window(
            self.specification.width, self.specification.height, self.specification.title, None, None)

    def _create_window_fullscreen(self) -> None:
        mon = glfw.get_primary_monitor()
        mode = glfw.get_video_mode(mon)

        glfw.window_hint(glfw.RED_BITS, mode.bits.red)
        glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
        glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
        glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

        self._handle = glfw.create_window(
            self.specification.width, self.specification.height, self.specification.title, mon, None)

    def _set_default_window_flags(self) -> None:
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, _OPENGL_VER_MAJOR)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, _OPENGL_VER_MINOR)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SAMPLES, self.specification.samples)

    @property
    def frametime(self) -> float:
        return self._renderer.info.frametime

    @property
    def renderer(self) -> Renderer:
        return self._renderer
