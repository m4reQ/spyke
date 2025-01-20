import typing as t

import imgui

from spyke_editor.ui.inspector import Inspector


class InspectorWindow:
    def __init__(self, inspectors: dict[type, Inspector]) -> None:
        self._selected_item: t.Any | None = None
        self._inspectors = inspectors
        self._current_inspector: Inspector | None = None

    def set_selected_item(self, item: t.Any) -> None:
        self._selected_item = item
        self._current_inspector = self._inspectors.get(type(item), None)

    def render(self) -> None:
        with imgui.begin('Inspector'):
            if self._current_inspector is None or self._selected_item is None:
                return

            imgui.text_unformatted(type(self._selected_item).__name__)
            imgui.separator()

            if self._current_inspector is not None:
                self._current_inspector.render(self._selected_item)
