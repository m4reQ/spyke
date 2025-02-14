import imgui
from pygl.math import Vector4

from spyke import debug, events
from spyke.graphics import renderer, window
from spyke_editor.ui.editor_panel import EditorPanel


class RendererInfoPanel(EditorPanel):
    def __init__(self) -> None:
        self.clear_color_changed = events.Event[Vector4]()

        self.frametime = 1.0
        self.clear_color = (0.0, 0.0, 0.0, 1.0)

    @debug.profiled
    def render(self) -> None:
        with imgui.begin('Renderer'):
            imgui.text_unformatted(f'Framebuffer size: {renderer.get_framebuffer_width()}x{renderer.get_framebuffer_height()}')
            imgui.text_unformatted(f'Window size: {window.get_width()}x{window.get_height()}')
            imgui.text_unformatted(f'Frametime: {(self.frametime * 1000.0):.2f} ms')
            imgui.text_unformatted(f'FPS: {(1.0 / self.frametime):.1f}')
            imgui.separator()

            clear_color_changed, new_clear_color  = imgui.color_edit4(
                'Clear color',
                *self.clear_color,
                imgui.COLOR_EDIT_NO_PICKER | imgui.COLOR_EDIT_NO_SIDE_PREVIEW)
            if clear_color_changed:
                self.clear_color = new_clear_color
                self.clear_color_changed.invoke(Vector4(*new_clear_color))
