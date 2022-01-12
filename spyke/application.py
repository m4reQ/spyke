# from . import enginePreview
from spyke.events.types import ToggleVsyncEvent
from spyke.graphics.gl import GLObject
from spyke.graphics.rendering import Renderer
from spyke import debug
from spyke import resourceManager
from spyke import events
from spyke.graphics import Renderer
from spyke.exceptions import GraphicsException, SpykeException
from spyke.constants import _OPENGL_VER_MAJOR, _OPENGL_VER_MINOR, DEFAULT_ICON_FILEPATH
from spyke.graphics.windowSpecs import WindowSpecs

import time
import glm
import glfw
import os
import gc
from PIL import Image
from abc import ABC, abstractmethod


class Application(ABC):
    def __init__(self, specification: WindowSpecs):
        start = time.perf_counter()

        if not glfw.init():
            raise GraphicsException('Cannot initialize GLFW.')

        glfw.set_error_callback(self._glfw_error_callback)

        self._set_default_window_flags(specification)

        if specification.fullscreen:
            self._handle = self._create_window_fullscreen(specification)
            debug.log_info('Window started in fullscreen mode.')
        else:
            self._handle = self._create_window_normal(specification)

        glfw.make_context_current(self._handle)

        # TODO: Implement this at some point
        # enginePreview.RenderPreview()
        # glfw.swap_buffers(self._handle)

        glfw.set_input_mode(self._handle, glfw.CURSOR,
                            glfw.CURSOR_NORMAL if specification.cursor_visible else glfw.CURSOR_HIDDEN)

        glfw.set_framebuffer_size_callback(self._handle, self._resize_cb)
        glfw.set_cursor_pos_callback(self._handle, self._cursor_pos_callback)
        glfw.set_window_iconify_callback(self._handle, self._iconify_callback)
        glfw.set_mouse_button_callback(self._handle, self._mouse_callback)
        glfw.set_scroll_callback(self._handle, self._mouse_scroll_callback)
        glfw.set_key_callback(self._handle, self._key_callback)
        glfw.set_window_pos_callback(self._handle, self._window_pos_callback)
        glfw.set_window_focus_callback(
            self._handle, self._window_focus_callback)

        events.register_method(self._toggle_vsync_callback,
                               ToggleVsyncEvent, priority=-1)

        # TODO: Move this to resource manager
        if specification.icon_filepath:
            if not os.path.endswith('.ico'):
                raise SpykeException(
                    f'Invalid icon extension: {os.path.splitext(specification.icon_filepath)}.')

            self._load_icon(specification.icon_filepath)
        else:
            self._load_icon(DEFAULT_ICON_FILEPATH)

        self._renderer = Renderer()
        # TODO: Move this to `Renderer` class
        self._renderer.info._get(self._handle)
        self._renderer.initialize()

        self.set_vsync(specification.vsync)

        gc.collect()

        debug.log_info(
            f'GLFW window initialized in {time.perf_counter() - start} seconds.')

    @abstractmethod
    def on_frame(self):
        pass

    @abstractmethod
    def on_close(self):
        pass

    @abstractmethod
    def on_load(self):
        pass

    def set_title(self, title: str) -> None:
        glfw.set_window_title(self._handle, title)

    def set_vsync(self, value: bool) -> None:
        glfw.swap_interval(int(value))
        debug.log_info(f'Vsync set to: {value}.')

    def _run(self):
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
            scene.Process(dt=self._renderer.info.frametime)

            if self._renderer.stats.window_active:
                # TODO: Create camera component and default primary camera entity (for now using identity matrix)
                self._renderer.render_scene(scene, glm.mat4(1.0))
                self.on_frame()
                glfw.swap_buffers(self._handle)

            glfw.poll_events()

            self._renderer.info.frametime = glfw.get_time() - start

        self.on_close()
        self._close()

    def _glfw_error_callback(self, code: int, message: str) -> None:
        raise GraphicsException(f'GLFW error: {message} ({code}).')

    def _resize_cb(self, _, width, height):
        events.invoke(events.ResizeEvent(width, height))

        debug.log_info(f'Window resized to ({width}, {height})')

    def _window_focus_callback(self, _, value):
        if value:
            events.invoke(events.WindowFocusEvent())
        else:
            events.invoke(events.WindowLostFocusEvent())

    def _cursor_pos_callback(self, _, x, y):
        events.invoke(events.MouseMoveEvent(x, y))

    def _window_pos_callback(self, _, x, y):
        self._renderer.info.window_position_x = x
        self._renderer.info.window_position_y = y

        events.invoke(events.WindowMoveEvent(x, y))

    def _iconify_callback(self, _, value):
        if value:
            events.invoke(events.WindowLostFocusEvent())
            self._renderer.info.window_active = False
        else:
            events.invoke(events.WindowFocusEvent())
            self._renderer.info.window_active = True

    def _mouse_callback(self, _, button, action, mods):
        if action == glfw.PRESS:
            events.invoke(events.MouseButtonDownEvent(button))
        elif action == glfw.RELEASE:
            events.invoke(events.MouseButtonUpEvent(button))

    def _mouse_scroll_callback(self, _, xOffset, yOffset):
        events.invoke(events.MouseScrollEvent(xOffset, yOffset))

    def _key_callback(self, _, key, scancode, action, mods):
        if action == glfw.PRESS:
            events.invoke(events.KeyDownEvent(key, mods, False))
        elif action == glfw.REPEAT:
            events.invoke(events.KeyDownEvent(key, mods, True))
        elif action == glfw.RELEASE:
            events.invoke(events.KeyUpEvent(key))

    def _toggle_vsync_callback(self, e: ToggleVsyncEvent):
        self.set_vsync(e.state)

    # TODO: Move this somewhere else. Maybe to resource manager
    def _load_icon(self, filepath: str) -> None:
        img = Image.open(filepath)
        glfw.set_window_icon(self._handle, 1, img)
        img.close()

    def _close(self):
        GLObject.delete_all()

        glfw.destroy_window(self._handle)
        debug.log_info('Window destroyed.')

        glfw.terminate()
        debug.log_info('Glfw terminated.')

    def _create_window_normal(self, spec):
        glfw.window_hint(glfw.RESIZABLE, spec.resizable)
        glfw.window_hint(glfw.DECORATED, not spec.borderless)

        return glfw.create_window(spec.width, spec.height, spec.title, None, None)

    def _create_window_fullscreen(self, spec):
        mon = glfw.get_primary_monitor()
        mode = glfw.get_video_mode(mon)

        glfw.window_hint(glfw.RED_BITS, mode.bits.red)
        glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
        glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
        glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)

        return glfw.create_window(spec.width, spec.height, spec.title, mon, None)

    def _set_default_window_flags(self, spec):
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, _OPENGL_VER_MAJOR)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, _OPENGL_VER_MINOR)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.SAMPLES, spec.samples)

    # TODO: Add getters for most frequently used statistice (like frametime, drawtime, etc.)
