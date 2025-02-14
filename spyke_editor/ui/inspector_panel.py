import typing as t

import imgui

from spyke import debug
from spyke.ecs import SpriteComponent, TagComponent, TransformComponent
from spyke_editor.ui.editor_panel import EditorPanel
from spyke_editor.ui.inspector import Inspector
from spyke_editor.ui.inspector_sprite import SpriteComponentInspector
from spyke_editor.ui.inspector_tag import TagComponentInspector
from spyke_editor.ui.inspector_transform import TransformComponentInspector


class InspectorPanel(EditorPanel):
    def __init__(self) -> None:
        self._inspectors: t.Mapping[type, Inspector] = {
            SpriteComponent: SpriteComponentInspector(),
            TagComponent: TagComponentInspector(),
            TransformComponent: TransformComponentInspector()}
        self._selected_item: t.Any | None = None
        self._current_inspector: Inspector | None = None

    def set_selected_item(self, item: t.Any) -> None:
        self._selected_item = item
        self._current_inspector = self._inspectors.get(type(item), None)

    @debug.profiled
    def render(self) -> None:
        with imgui.begin('Inspector'):
            if self._current_inspector is None or self._selected_item is None:
                return

            imgui.text_unformatted(type(self._selected_item).__name__)
            imgui.separator()

            if self._current_inspector is not None:
                self._current_inspector.render(self._selected_item)

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        pass
