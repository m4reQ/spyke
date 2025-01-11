import imgui

from spyke.ecs.components.tag import TagComponent
from spyke_editor.ui.inspector import Inspector


class TagComponentInspector(Inspector[TagComponent]):
    def get_supported_types(self) -> tuple[type]:
        return (TagComponent,)

    def render(self, item: TagComponent) -> None:
        name_changed, new_name = imgui.input_text(
            'Name',
            item.name)
        if name_changed:
            item.name = new_name
