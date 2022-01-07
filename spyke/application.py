# from . import enginePreview
from spyke.graphics.gl import GLObject
from spyke import debug
from spyke import resourceManager
from spyke import events
from spyke.enums import Keys
from spyke.graphics import Renderer
from spyke.exceptions import GraphicsException, SpykeException
from spyke.imgui import Imgui
from spyke.constants import _OPENGL_VER_MAJOR, _OPENGL_VER_MINOR, DEFAULT_ICON_FILEPATH
from spyke.windowSpecs import WindowSpecs

import time
import glm
import atexit
import glfw
import os
import gc
from PIL import Image
from abc import ABC, abstractmethod


class FrameStats:
    # TODO: Move this somewhere else

    __slots__ = (
        '__weakref__',
        'frametime',
        'drawtime',
        'draw_calls',
        'vertex_count',
        'window_active'
    )

    def __init__(self):
        self.frametime: float = 1.0
        self.drawtime: float = 0.0
        self.draw_calls: int = 0
        self.vertex_count: int = 0
        self.window_active: bool = True


class Application(ABC):
    def __init__(self, specification: WindowSpecs, startImgui: bool = False):
        start = time.perf_counter()

        # TODO: Move all window-related statistics objects here.
        # TODO: Make renderer instanciable and do something with it
        self.frame_stats = FrameStats()

        if not glfw.init():
            raise GraphicsException("Cannot initialize GLFW.")

        glfw.set_error_callback(self._glfw_error_callback)

        # TODO: Move this functionality to some other place (maybe RendererInfo?)
        ver = '.'.join(str(x) for x in glfw.get_version())
        debug.log_info(f'GLFW version: {ver}')

        self._set_default_window_flags(specification)

        if specification.fullscreen:
            self._handle = self._create_window_fullscreen(specification)
            debug.log_info('Window started in fullscreen mode.')
        else:
            self._handle = self._create_window_normal(specification)

        glfw.make_context_current(self._handle)

        self._get_screen_info(specification)

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

        if specification.icon_filepath:
            if not os.path.endswith('.ico'):
                raise SpykeException(
                    f'Invalid icon extension: {os.path.splitext(specification.icon_filepath)}.')

            self._load_icon(specification.icon_filepath)
        else:
            self._load_icon(DEFAULT_ICON_FILEPATH)

        self.set_vsync(specification.vsync)

        # TODO: Move this to RendererInfo
        self.position_x, self.position_y = glfw.get_window_pos(self._handle)

        Renderer.Initialize(Renderer.screenStats.width,
                            Renderer.screenStats.height, specification.samples)

        if startImgui:
            Imgui.Initialize()
            atexit.register(Imgui.Close)

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
        Renderer.screenStats.vsync = value

        debug.log_info(f'Vsync set to: {value}.')

    def run(self):
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

            Imgui._OnFrame()

            resourceManager.GetCurrentScene().Process(dt=self.frame_stats.frametime)

            if self.frame_stats.window_active:
                # TODO: Crete camera component and default primary camera entity (for now using identity matrix)
                Renderer.RenderScene(
                    resourceManager.GetCurrentScene(), glm.mat4(1.0))
                self.on_frame()
                glfw.swap_buffers(self._handle)

            glfw.poll_events()

            self.frame_stats.frametime = glfw.get_time() - start

        self.on_close()

        # TODO: Make this invoked by the event system with priority -1
        self._close()

    def _glfw_error_callback(self, code: int, message: str) -> None:
        raise GraphicsException(f'GLFW error: {message} ({code}).')

    def _resize_cb(self, _, width, height):
        # TODO: Move this functionality to RendererInfo class
        Renderer.screenStats.width = width
        Renderer.screenStats.height = height

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
        self.position_x = x
        self.position_y = y

        events.invoke(events.WindowMoveEvent(x, y))

    def _iconify_callback(self, _, value):
        if value:
            events.invoke(events.WindowLostFocusEvent())
            self.frame_stats.window_active = False
        else:
            events.invoke(events.WindowFocusEvent())
            self.frame_stats.window_active = True

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
            if key == Keys.KeyF2:
                self.set_vsync(not Renderer.screenStats.vsync)
        elif action == glfw.REPEAT:
            events.invoke(events.KeyDownEvent(key, mods, True))
        elif action == glfw.RELEASE:
            events.invoke(events.KeyUpEvent(key))

    # TODO: Move this somewhere else. Maybe to resource manager
    def _load_icon(self, filepath: str) -> None:
        img = Image.open(filepath)
        glfw.set_window_icon(self._handle, 1, img)
        img.close()

    def _close(self):
        atexit.unregister(Imgui.Close)
        Imgui.Close()

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

    def _get_screen_info(self, spec):
        # TODO: Move this functionality to RendererInfo class
        Renderer.screenStats.width, Renderer.screenStats.height = glfw.get_framebuffer_size(
            self._handle)

        vidmode = glfw.get_video_mode(glfw.get_primary_monitor())
        Renderer.screenStats.refresh_rate = vidmode.refresh_rate
        Renderer.screenStats.vsync = spec.vsync
