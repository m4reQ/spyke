import typing as t

import imgui

from spyke import debug, events
from spyke.ecs import Component, Scene, TagComponent
from spyke_editor.ui.editor_panel import EditorPanel


class SceneHierarchyPanel(EditorPanel):
    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.selection_changed = events.Event[t.Any]()

    @debug.profiled
    def render(self) -> None:
        with imgui.begin('Scene'):
            for entity in self.scene.get_entities():
                entity_components = self.scene.get_components_for_entity(entity)
                if imgui.tree_node(_get_entity_name(entity, entity_components), imgui.TREE_NODE_DEFAULT_OPEN):
                    for component in entity_components:
                        imgui.tree_node(type(component).__name__, imgui.TREE_NODE_LEAF | imgui.TREE_NODE_NO_TREE_PUSH_ON_OPEN)

                        if imgui.is_item_clicked():
                            self.selection_changed.invoke(component)

                    imgui.tree_pop()

def _get_entity_name(entity: int, entity_components: t.Iterable[Component]) -> str:
    for comp in entity_components:
        if isinstance(comp, TagComponent):
            return comp.name

    return str(entity)
