import typing as t

import imgui

from spyke import debug
from spyke.ecs import Scene
from spyke.graphics import camera, renderer
from spyke_editor.ui.editor_panel import EditorPanel


class ScenePreviewPanel(EditorPanel):
    def __init__(self, scene: Scene):
        self._scene = scene

    @debug.profiled
    def render(self) -> None:
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))

        with imgui.begin(self._scene.name):
            imgui.pop_style_var(1)

            content_region = imgui.get_content_region_available()
            content_width = int(content_region.x)
            content_height = int(content_region.y)

            if isinstance(self._scene.camera, camera.PerspectiveCamera):
                self._scene.camera.fov = content_width / content_height

            imgui.image(renderer.get_framebuffer_color_texture_id(), content_region.x, content_region.y)
