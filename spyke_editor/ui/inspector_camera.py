import imgui

from spyke.ecs.components.camera import CameraComponent, CameraType
from spyke_editor.ui.inspector import Inspector

_DRAG_SPEED_SLOW = 0.001

class CameraComponentInspector(Inspector[CameraComponent]):
    def __init__(self):
        super().__init__()

        self._camera_types = {
            CameraType.PERSPECTIVE.name: CameraType.PERSPECTIVE,
            CameraType.ORTHO.name: CameraType.ORTHO}

    def get_supported_types(self) -> tuple[type]:
        return (CameraComponent,)

    def render(self, item: CameraComponent) -> None:
        if imgui.begin_combo('Type', item.type.name):
            for type_name, camera_type in self._camera_types.items():
                _, is_selected = imgui.selectable(type_name)

                if is_selected:
                    item.type = camera_type
                    imgui.set_item_default_focus()

            imgui.end_combo()

        imgui.separator()

        fov_changed, new_fov = imgui.drag_float('FOV', item.fov, _DRAG_SPEED_SLOW)
        if fov_changed:
            item.fov = new_fov

        aspect_changed, new_aspect = imgui.drag_float('Aspect ratio', item.aspect, _DRAG_SPEED_SLOW)
        if aspect_changed:
            item.aspect = new_aspect

        imgui.separator()

        imgui.text_unformatted('Viewport')

        view_x_changed, new_view_x = imgui.drag_float('X', item.viewport.x, _DRAG_SPEED_SLOW)
        if view_x_changed:
            item.viewport.x = new_view_x
            item._needs_recalculate = True # TODO Respond to viewport being only partially changed

        view_y_changed, new_view_y = imgui.drag_float('Y', item.viewport.y, _DRAG_SPEED_SLOW)
        if view_y_changed:
            item.viewport.y = new_view_y
            item._needs_recalculate = True

        view_w_changed, new_view_w = imgui.drag_float('Width', item.viewport.width, _DRAG_SPEED_SLOW)
        if view_w_changed:
            item.viewport.width = new_view_w
            item._needs_recalculate = True

        view_h_changed, new_view_h = imgui.drag_float('Height', item.viewport.height, _DRAG_SPEED_SLOW)
        if view_h_changed:
            item.viewport.height = new_view_h
            item._needs_recalculate = True
