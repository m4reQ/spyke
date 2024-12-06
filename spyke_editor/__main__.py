import glfw
import imgui

from pygl import commands
from spyke import application, debug, events
from spyke.enums import Key, KeyMod
from spyke.graphics import renderer, window
from spyke_editor.imgui_pygl_backend import PYGLBackend


class EditorApplication(application.Application):
    def __init__(self) -> None:
        super().__init__(window.WindowSpec(1080, 720, 'Spyke Editor', vsync=True))

        self._imgui_backend: PYGLBackend

    @debug.profiled('editor')
    def on_load(self) -> None:
        super().on_load()

        _initialize_imgui()
        self._imgui_backend = _create_imgui_backend()

    def on_close(self) -> None:
        super().on_close()

        self._imgui_backend.shutdown()

    @debug.profiled('editor')
    def on_frame(self, frametime: float) -> None:
        super().on_frame(frametime)

        io = imgui.get_io()
        io.delta_time = frametime

        imgui.new_frame()
        imgui.show_test_window()
        imgui.render()

        commands.viewport(0, 0, window.get_width(), window.get_height())
        commands.scissor(0, 0, window.get_width(), window.get_height())

        renderer.clear()
        self._imgui_backend.render(imgui.get_draw_data())

        window.swap_buffers()

@debug.profiled('editor')
def _create_imgui_backend() -> PYGLBackend:
    return PYGLBackend()

@debug.profiled('editor')
def _setup_imgui_input() -> None:
    io = imgui.get_io()
    io.key_map[imgui.KEY_TAB] = Key.Tab
    io.key_map[imgui.KEY_LEFT_ARROW] = Key.Left
    io.key_map[imgui.KEY_RIGHT_ARROW] = Key.Right
    io.key_map[imgui.KEY_UP_ARROW] = Key.Up
    io.key_map[imgui.KEY_DOWN_ARROW] = Key.Down
    io.key_map[imgui.KEY_PAGE_UP] = Key.PageUp
    io.key_map[imgui.KEY_PAGE_DOWN] = Key.PageDown
    io.key_map[imgui.KEY_HOME] = Key.Home
    io.key_map[imgui.KEY_END] = Key.End
    io.key_map[imgui.KEY_INSERT] = Key.Insert
    io.key_map[imgui.KEY_DELETE] = Key.Delete
    io.key_map[imgui.KEY_BACKSPACE] = Key.Backspace
    io.key_map[imgui.KEY_SPACE] = Key.Space
    io.key_map[imgui.KEY_ENTER] = Key.Enter
    io.key_map[imgui.KEY_ESCAPE] = Key.Escape
    # io.key_map[imgui.KEY_PAD_ENTER] FIXME NO ENUM !
    io.key_map[imgui.KEY_A] = Key.A
    io.key_map[imgui.KEY_C] = Key.C
    io.key_map[imgui.KEY_V] = Key.V
    io.key_map[imgui.KEY_X] = Key.X
    io.key_map[imgui.KEY_Y] = Key.Y
    io.key_map[imgui.KEY_Z] = Key.Z

    events.register(_imgui_key_down_callback, events.KeyDownEvent, priority=1)
    events.register(_imgui_key_up_callback, events.KeyUpEvent, priority=1)
    events.register(_imgui_resize_callback, events.ResizeEvent, priority=1)
    events.register(_imgui_mouse_callback, events.MouseMoveEvent, priority=1)
    events.register(_imgui_mouse_button_down_callback, events.MouseButtonDownEvent, priority=1)
    events.register(_imgui_mouse_button_up_callback, events.MouseButtonUpEvent, priority=1)

def _imgui_key_up_callback(event: events.KeyUpEvent) -> None:
    io = imgui.get_io()
    io.keys_down[event.key] = False

def _imgui_key_down_callback(event: events.KeyDownEvent) -> None:
    io = imgui.get_io()
    io.keys_down[event.key] = True

    _imgui_update_key_mods(KeyMod(event.mods))
    _imgui_update_char_input(event.scancode) # TODO events.CharEvent (glfw.set_char_callback)

def _imgui_update_key_mods(mods: KeyMod) -> None:
    io = imgui.get_io()

    io.key_ctrl = KeyMod.Control in mods
    io.key_alt = KeyMod.Alt in mods
    io.key_shift = KeyMod.Shift in mods
    io.key_super = KeyMod.Super in mods

def _imgui_update_char_input(char: int) -> None:
    io = imgui.get_io()
    if 0 < char < 0x10000:
        io.add_input_character(char)

def _imgui_resize_callback(event: events.ResizeEvent) -> None:
    io = imgui.get_io()
    io.display_size = event.size
    io.display_fb_scale = _compute_fb_scale(event.width, event.height, event.width, event.height)

def _imgui_mouse_callback(event: events.MouseMoveEvent) -> None:
    io = imgui.get_io()
    io.mouse_pos = event.position

def _imgui_mouse_button_down_callback(event: events.MouseButtonDownEvent) -> None:
    io = imgui.get_io()
    io.mouse_down[event.button] = True

def _imgui_mouse_button_up_callback(event: events.MouseButtonUpEvent) -> None:
    io = imgui.get_io()
    io.mouse_down[event.button] = False

@debug.profiled('editor', 'initialization')
def _initialize_imgui() -> None:
    imgui.create_context()
    imgui.style_colors_dark()

    io = imgui.get_io()
    io.display_size = (window.get_width(), window.get_height())

    _setup_imgui_input()

def _compute_fb_scale(window_width: int, window_height: int, fb_width: int, fb_height: int) -> tuple[float, float]:
    if window_width != 0 and window_height != 0:
        return (fb_width / window_width, fb_height / window_height)

    return (1.0, 1.0)

if __name__ == '__main__':
    app = EditorApplication()
    app.run()
