import os

import imgui
from pygl.math import Vector4

from spyke import debug, input
from spyke.ecs import Scene
from spyke.events import Event
from spyke.graphics import window
from spyke_editor import imgui_renderer
from spyke_editor.ui.assets_panel import AssetsPanel
from spyke_editor.ui.inspector_panel import InspectorPanel
from spyke_editor.ui.renderer_info_panel import RendererInfoPanel
from spyke_editor.ui.scene_hierarchy_panel import SceneHierarchyPanel
from spyke_editor.ui.scene_preview_panel import ScenePreviewPanel

_BUTTON_MAP = {
    input.Button.LEFT: 0,
    input.Button.RIGHT: 1}

@debug.profiled
def initialize(scene: Scene) -> None:
    global _hierarchy_panel, _assets_panel, _renderer_panel, _inspector_panel, _preview_panel

    _initialize_imgui()
    imgui_renderer.initialize()

    _hierarchy_panel = SceneHierarchyPanel(scene)
    _preview_panel = ScenePreviewPanel(scene)
    _assets_panel = AssetsPanel(os.getcwd())
    _renderer_panel = RendererInfoPanel()
    _inspector_panel = InspectorPanel()

    _hierarchy_panel.selection_changed.subscribe(lambda x: _inspector_panel.set_selected_item(x))

@debug.profiled
def update(frametime: float) -> None:
    imgui.get_io().delta_time = frametime

    _renderer_panel.frametime = frametime

@debug.profiled
def render() -> None:
    imgui.new_frame()

    _enable_dockspace('main')
    _hierarchy_panel.render()
    _assets_panel.render()
    _renderer_panel.render()
    _preview_panel.render()
    _inspector_panel.render()

    imgui.render()
    imgui_renderer.render(imgui.get_draw_data(), (0.0, 0.0, 0.0, 1.0))

def clear_color_changed() -> Event[Vector4]:
    return _renderer_panel.clear_color_changed

def _enable_dockspace(name: str) -> None:
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

@debug.profiled
def _initialize_imgui() -> None:
    imgui.create_context()
    imgui.style_colors_dark()

    io = imgui.get_io()
    io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
    io.display_size = (window.get_width(), window.get_height())
    io.key_map[imgui.KEY_TAB] = input.Key.TAB
    io.key_map[imgui.KEY_LEFT_ARROW] = input.Key.LEFT
    io.key_map[imgui.KEY_RIGHT_ARROW] = input.Key.RIGHT
    io.key_map[imgui.KEY_UP_ARROW] = input.Key.UP
    io.key_map[imgui.KEY_DOWN_ARROW] = input.Key.DOWN
    io.key_map[imgui.KEY_PAGE_UP] = input.Key.PRIOR
    io.key_map[imgui.KEY_PAGE_DOWN] = input.Key.NEXT
    io.key_map[imgui.KEY_HOME] = input.Key.HOME
    io.key_map[imgui.KEY_END] = input.Key.END
    io.key_map[imgui.KEY_INSERT] = input.Key.INSERT
    io.key_map[imgui.KEY_DELETE] = input.Key.DELETE
    io.key_map[imgui.KEY_BACKSPACE] = input.Key.BACK
    io.key_map[imgui.KEY_SPACE] = input.Key.SPACE
    io.key_map[imgui.KEY_ENTER] = input.Key.RETURN
    io.key_map[imgui.KEY_ESCAPE] = input.Key.ESCAPE
    # TODO Support handling of numpad enter, right alt and ctrl inside `input`. Use bit 24 on WM_KEY(UP|DOWN)
    io.key_map[imgui.KEY_PAD_ENTER] = input.Key.RETURN
    io.key_map[imgui.KEY_A] = input.Key.A
    io.key_map[imgui.KEY_C] = input.Key.C
    io.key_map[imgui.KEY_V] = input.Key.V
    io.key_map[imgui.KEY_X] = input.Key.X
    io.key_map[imgui.KEY_Y] = input.Key.Y
    io.key_map[imgui.KEY_Z] = input.Key.Z

    window.key_down_event.subscribe(_imgui_key_down_callback)
    window.key_up_event.subscribe(_imgui_key_up_callback)
    window.resize_event.subscribe(_imgui_resize_callback)
    window.mouse_move_event.subscribe(_imgui_mouse_callback)
    window.button_down_event.subscribe(_imgui_mouse_button_down_callback)
    window.button_up_event.subscribe(_imgui_mouse_button_up_callback)
    # TODO Allow access to integer character value of CharEventData
    window.scroll_event.subscribe(_imgui_scroll_callback)
    window.char_event.subscribe(_imgui_char_event)

def _imgui_char_event(event: window.CharEventData) -> None:
    io = imgui.get_io()
    io.add_input_character(ord(event.character))

def _imgui_scroll_callback(event: window.ScrollEventData) -> None:
    io = imgui.get_io()
    io.mouse_wheel = event.delta * io.delta_time

def _imgui_key_up_callback(event: window.KeyUpEventData) -> None:
    io = imgui.get_io()
    io.keys_down[event.key] = False

def _imgui_key_down_callback(event: window.KeyDownEventData) -> None:
    # TODO Allow getting modifiers from keydown event (Win32)
    io = imgui.get_io()
    io.keys_down[event.key] = True
    io.key_ctrl = input.is_modifier_active(input.Modifier.CONTROL)
    # FIXME Cannot check for alt
    # io.key_alt = input.is_modifier_active(Modifier.ALT)
    io.key_shift = input.is_modifier_active(input.Modifier.SHIFT)
    # FIXME Cannot check for "SUPER" (whatever it means)
    # io.key_super = input.is_modifier_active(Modifier.)

def _imgui_resize_callback(event: window.ResizeEventData) -> None:
    io = imgui.get_io()
    io.display_size = event.size
    io.display_fb_scale = (1.0, 1.0)

def _imgui_mouse_callback(event: window.MouseMoveEventData) -> None:
    io = imgui.get_io()
    io.mouse_pos = event.position

def _imgui_mouse_button_down_callback(event: window.ButtonDownEventData) -> None:
    io = imgui.get_io()
    io.mouse_down[_translate_button(event.button)] = True

def _imgui_mouse_button_up_callback(event: window.ButtonUpEventData) -> None:
    io = imgui.get_io()
    io.mouse_down[_translate_button(event.button)] = False

def _translate_button(button: input.Button) -> int:
    return _BUTTON_MAP[button]

_hierarchy_panel: SceneHierarchyPanel
_assets_panel: AssetsPanel
_renderer_panel: RendererInfoPanel
_preview_panel: ScenePreviewPanel
_inspector_panel: InspectorPanel
