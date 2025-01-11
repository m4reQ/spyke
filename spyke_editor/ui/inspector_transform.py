import imgui

from pygl.math import Vector3
from spyke.ecs.components.transform import TransformComponent
from spyke_editor.ui.inspector import Inspector

_DRAG_SPEED_SLOW = 0.001
_DRAG_SPEED_FAST = 0.1

class TransformComponentInspector(Inspector[TransformComponent]):
    def get_supported_types(self):
        return (TransformComponent,)

    def render(self, item: TransformComponent) -> None:
        # TODO Customizable drag speed

        pos_changed, new_pos = imgui.drag_float3(
            'Position',
            *item.position,
            _DRAG_SPEED_SLOW)
        if pos_changed:
            item.position = Vector3(*new_pos)

        size_changed, new_scale = imgui.drag_float3(
            'Scale',
            *item.scale,
            _DRAG_SPEED_SLOW)
        if size_changed:
            item.scale = Vector3(*new_scale)

        rotation_changed, new_rotation = imgui.drag_float3(
            'Rotation',
            *item.rotation,
            _DRAG_SPEED_FAST,
            0.0,
            360.0)
        if rotation_changed:
            item.rotation = Vector3(*new_rotation)
