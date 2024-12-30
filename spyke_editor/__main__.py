import imgui

from pygl import commands
from pygl.math import Matrix4, Vector3, Vector4
from spyke import application, debug, events, resources
from spyke.enums import Key, KeyMod
from spyke.graphics import renderer, window
from spyke_editor import imgui_renderer


class EditorApplication(application.Application):
    def __init__(self) -> None:
        super().__init__(window.WindowSpec(1080, 720, 'Spyke Editor', vsync=True))

        self._framebuffer_clear_color = (0.0, 0.0, 0.0, 1.0)

    @debug.profiled('editor')
    def on_load(self) -> None:
        events.register(_renderer_resize_callback, events.ResizeEvent, priority=1)

        _initialize_imgui()
        imgui_renderer.initialize()

    def on_close(self) -> None:
        imgui_renderer.shutdown()

    @debug.profiled('editor')
    def on_update(self, frametime: float) -> None:
        imgui.get_io().delta_time = frametime

        fb_width = window.get_framebuffer_width()
        fb_height = window.get_framebuffer_height()

        imgui.new_frame()

        enable_dockspace('main')

        with imgui.begin('Framebuffer'):
            content_region = imgui.get_content_region_available()
            renderer.resize(int(content_region.x), int(content_region.y))

            imgui.image(renderer.get_framebuffer_color_texture_id(), content_region.x, content_region.y)

        with imgui.begin('Renderer'):
            imgui.text_unformatted('Frame info:')
            imgui.text_unformatted(f'Framebuffer size: {fb_width}x{fb_height}')
            imgui.text_unformatted(f'Frametime: {(frametime * 1000.0):.2f} ms')
            imgui.text_unformatted(f'FPS: {(1.0 / frametime):.1f}')
            imgui.separator()

            _, self._framebuffer_clear_color = imgui.color_edit4(
                'Clear color',
                *self._framebuffer_clear_color,
                imgui.COLOR_EDIT_NO_PICKER | imgui.COLOR_EDIT_NO_SIDE_PREVIEW)

        with imgui.begin('Assets'):
            pass

        imgui.render()

    @debug.profiled('editor')
    def on_render(self, frametime: float) -> None:
        fb_width = window.get_framebuffer_width()
        fb_height = window.get_framebuffer_height()

        # main render pass
        renderer.begin_frame()
        commands.scissor(0, 0, fb_width, fb_height)
        renderer.clear(Vector4(*self._framebuffer_clear_color))
        renderer.begin_batch(resources.get(resources.Model.quad, resources.Model))
        renderer.render(Vector4(1.0), Matrix4.transform(Vector3(0.0), Vector3(0.5, 0.5, 0.0)))
        renderer.end_batch()
        renderer.end_frame()

        # imgui render pass
        commands.scissor(0, 0, fb_width, fb_height)
        renderer.clear(Vector4(0.0, 0.0, 0.0, 1.0))
        imgui_renderer.render(imgui.get_draw_data())

        window.swap_buffers()

@debug.profiled('editor', 'imgui')
def _initialize_imgui() -> None:
    imgui.create_context()
    imgui.style_colors_dark()

    io = imgui.get_io()
    io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
    io.display_size = (window.get_framebuffer_width(), window.get_framebuffer_height())

    _setup_imgui_keymap(io.key_map)
    _setup_imgui_callbacks()

@debug.profiled('editor', 'imgui')
def _setup_imgui_callbacks() -> None:
    events.register(_imgui_key_down_callback, events.KeyDownEvent, priority=1)
    events.register(_imgui_key_up_callback, events.KeyUpEvent, priority=1)
    events.register(_imgui_resize_callback, events.ResizeEvent, priority=1)
    events.register(_imgui_mouse_callback, events.MouseMoveEvent, priority=1)
    events.register(_imgui_mouse_button_down_callback, events.MouseButtonDownEvent, priority=1)
    events.register(_imgui_mouse_button_up_callback, events.MouseButtonUpEvent, priority=1)
    events.register(_imgui_scroll_callback, events.MouseScrollEvent, priority=1)

@debug.profiled('editor', 'imgui')
def _setup_imgui_keymap(key_map: dict[int, int]) -> None:
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
