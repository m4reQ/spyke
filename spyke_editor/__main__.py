import imgui

from pygl import commands
from spyke import application, debug, events
from spyke.enums import Key, KeyMod
from spyke.graphics import renderer, window
from spyke_editor.imgui_pygl_backend import PYGLBackend


class EditorApplication(application.Application):
    def __init__(self) -> None:
        super().__init__(window.WindowSpec(1080, 720, 'Spyke Editor', vsync=False))

        self._imgui_backend: PYGLBackend

    @debug.profiled('editor')
    def on_load(self) -> None:
        events.register(_renderer_resize_callback, events.ResizeEvent, priority=1)

        _initialize_imgui()
        self._imgui_backend = _create_imgui_backend()

    def on_close(self) -> None:
        self._imgui_backend.shutdown()

    @debug.profiled('editor')
    def on_update(self, frametime: float) -> None:
        imgui.get_io().delta_time = frametime

        window.set_title(f'Spyke Editor | Frametime: {(frametime * 1000.0):.2f} ms | FPS: {(1.0 / frametime):.1f}')

    @debug.profiled('editor')
    def on_render(self, frametime: float) -> None:
        imgui.new_frame()

        enable_dockspace('main')

        with imgui.begin('Test Window'):
            imgui.text('Hello from test window')

        with imgui.begin('Test Window 2'):
            imgui.text('This docks inside')

        imgui.render()

        fb_width = window.get_framebuffer_width()
        fb_height = window.get_framebuffer_height()
        commands.scissor(0, 0, fb_width, fb_height)

        renderer.clear(False)

        self._imgui_backend.render(imgui.get_draw_data())

        window.swap_buffers()

@debug.profiled('editor')
def _create_imgui_backend() -> PYGLBackend:
    return PYGLBackend()

@debug.profiled('editor', 'initialization')
def _initialize_imgui() -> None:
    imgui.create_context()
    imgui.style_colors_light()

    io = imgui.get_io()
    io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
    io.display_size = (window.get_framebuffer_width(), window.get_framebuffer_height())

    _setup_imgui_input()

@debug.profiled('editor')
def _setup_imgui_input() -> None:
    key_map = imgui.get_io().key_map
    key_map[imgui.KEY_TAB] = Key.Tab
    key_map[imgui.KEY_LEFT_ARROW] = Key.Left
    key_map[imgui.KEY_RIGHT_ARROW] = Key.Right
    key_map[imgui.KEY_UP_ARROW] = Key.Up
    key_map[imgui.KEY_DOWN_ARROW] = Key.Down
    key_map[imgui.KEY_PAGE_UP] = Key.PageUp
    key_map[imgui.KEY_PAGE_DOWN] = Key.PageDown
    key_map[imgui.KEY_HOME] = Key.Home
    key_map[imgui.KEY_END] = Key.End
    key_map[imgui.KEY_INSERT] = Key.Insert
    key_map[imgui.KEY_DELETE] = Key.Delete
    key_map[imgui.KEY_BACKSPACE] = Key.Backspace
    key_map[imgui.KEY_SPACE] = Key.Space
    key_map[imgui.KEY_ENTER] = Key.Enter
    key_map[imgui.KEY_ESCAPE] = Key.Escape
    key_map[imgui.KEY_PAD_ENTER] = Key.KeypadEnter
    key_map[imgui.KEY_A] = Key.A
    key_map[imgui.KEY_C] = Key.C
    key_map[imgui.KEY_V] = Key.V
    key_map[imgui.KEY_X] = Key.X
    key_map[imgui.KEY_Y] = Key.Y
    key_map[imgui.KEY_Z] = Key.Z

    events.register(_imgui_key_down_callback, events.KeyDownEvent, priority=1)
    events.register(_imgui_key_up_callback, events.KeyUpEvent, priority=1)
    events.register(_imgui_resize_callback, events.ResizeEvent, priority=1)
    events.register(_imgui_mouse_callback, events.MouseMoveEvent, priority=1)
    events.register(_imgui_mouse_button_down_callback, events.MouseButtonDownEvent, priority=1)
    events.register(_imgui_mouse_button_up_callback, events.MouseButtonUpEvent, priority=1)
    events.register(_imgui_scroll_callback, events.MouseScrollEvent, priority=1)

def _imgui_scroll_callback(event: events.MouseScrollEvent) -> None:
    io = imgui.get_io()
    io.mouse_wheel_horizontal = event.x_offset
    io.mouse_wheel = event.y_offset

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
    io.display_fb_scale = _compute_fb_scale(
        event.width,
        event.height,
        event.framebuffer_width,
        event.framebuffer_height)

def _imgui_mouse_callback(event: events.MouseMoveEvent) -> None:
    io = imgui.get_io()
    io.mouse_pos = event.position

def _imgui_mouse_button_down_callback(event: events.MouseButtonDownEvent) -> None:
    io = imgui.get_io()
    io.mouse_down[event.button] = True

def _imgui_mouse_button_up_callback(event: events.MouseButtonUpEvent) -> None:
    io = imgui.get_io()
    io.mouse_down[event.button] = False

def _renderer_resize_callback(event: events.ResizeEvent) -> None:
    renderer.resize(event.framebuffer_width, event.framebuffer_height)

def _compute_fb_scale(window_width: int, window_height: int, fb_width: int, fb_height: int) -> tuple[float, float]:
    if window_width != 0 and window_height != 0:
        return (fb_width / window_width, fb_height / window_height)

    return (1.0, 1.0)

def enable_dockspace(name: str) -> None:
    flags = (
        imgui.WINDOW_NO_DOCKING |
        imgui.WINDOW_NO_TITLE_BAR |
        imgui.WINDOW_NO_COLLAPSE |
        imgui.WINDOW_NO_RESIZE |
        imgui.WINDOW_NO_MOVE |
        imgui.WINDOW_NO_BACKGROUND |
        imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS |
        imgui.WINDOW_NO_NAV_FOCUS)
    viewport = imgui.get_main_viewport()

    imgui.set_next_window_position(*viewport.pos)
    imgui.set_next_window_size(*viewport.size)
    imgui.set_next_window_viewport(viewport.id)
    imgui.push_style_var(imgui.STYLE_WINDOW_BORDERSIZE, 0.0)
    imgui.push_style_var(imgui.STYLE_WINDOW_ROUNDING, 0.0)
    imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))

    with imgui.begin(name, None, flags):
        imgui.pop_style_var(3)
        imgui.dockspace(
            imgui.get_id(name),
            (0, 0),
            imgui.DOCKNODE_PASSTHRU_CENTRAL_NODE)

if __name__ == '__main__':
    app = EditorApplication()
    app.run()
