import typing as t
import uuid

import imgui
import numpy as np

from pygl import commands, rendering
from pygl.math import Matrix4, Vector2, Vector3, Vector4
from pygl.rendering import ElementsType
from spyke import application, assets, debug, ecs, events
from spyke.assets.asset_source import AssetSource
from spyke.assets.loaders.dds_loader import DDSLoader
from spyke.assets.loaders.standard_image_loader import StandardImageLoader
from spyke.assets.types import Model
from spyke.assets.types.image import Image, ImageConfig
from spyke.ecs import components
from spyke.enums import Key, KeyMod
from spyke.graphics import renderer, window
from spyke.graphics.rectangle import Rectangle
from spyke_editor import imgui_renderer
from spyke_editor.ui.inspector_camera import CameraComponentInspector
from spyke_editor.ui.inspector_sprite import SpriteComponentInspector
from spyke_editor.ui.inspector_tag import TagComponentInspector
from spyke_editor.ui.inspector_transform import TransformComponentInspector
from spyke_editor.ui.inspector_window import InspectorWindow


class EditorApplication(application.Application):
    def __init__(self) -> None:
        super().__init__(window.WindowSpec(1080, 720, 'Spyke Editor', vsync=True))

        self._framebuffer_clear_color = (0.0, 0.0, 0.0, 1.0)
        self._scene = ecs.Scene('editor-main-scene')
        self._inspector_window = InspectorWindow({
            components.SpriteComponent: SpriteComponentInspector(),
            components.TagComponent: TagComponentInspector(),
            components.TransformComponent: TransformComponentInspector(),
            components.CameraComponent: CameraComponentInspector()})
        self._image1: uuid.UUID
        self._image2: uuid.UUID

        # default editor resources
        self._quad_model: uuid.UUID
        self._cube_model: uuid.UUID

    @debug.profiled('editor')
    def on_load(self) -> None:
        _initialize_assets()

        image_config = ImageConfig.default()
        image_config.mipmap_count = 2

        self._image1 = assets.load_from_file(Image, r'C:\Users\mmize\Desktop\_DSC0322.JPG', image_config)
        self._image2 = assets.load_from_file(Image, r'C:\Users\mmize\Desktop\_DSC0115.JPG', image_config)
        self._quad_model = assets.add_asset(_create_quad_model())
        self._cube_model = assets.add_asset(_create_cube_model())

        _initialize_imgui()
        imgui_renderer.initialize()

        self._scene.create_entity(
            components.TagComponent('C U B E'),
            components.SpriteComponent(Vector4(1.0), self._cube_model, Image.get_empty_asset()),
            components.TransformComponent(
                Vector3(0.0, 0.0, 0.1),
                Vector3(0.2, 0.2, 0.2),
                Vector3(0.0)))

        self._scene.create_entity(
            components.TagComponent('Image 1 Quad'),
            components.SpriteComponent(Vector4(1.0), self._quad_model, Image.get_empty_asset()),
            components.TransformComponent(
                Vector3(-0.2, -0.2, 0.2),
                Vector3(0.4, 0.2, 0.0),
                Vector3(0.0)))

        self._scene.create_entity(
            components.TagComponent('Image 2 Quad'),
            components.SpriteComponent(Vector4(1.0), self._quad_model, Image.get_empty_asset()),
            components.TransformComponent(
                Vector3(0.0, 0.3, 0.3),
                Vector3(0.5, 0.5, 0.1),
                Vector3(0.0)))

        camera_entity = self._scene.create_entity(
            components.TagComponent('Main Camera'),
            components.TransformComponent(
                Vector3(0.0, 0.0, 0.0),
                Vector3(1.0, 1.0, 0.0),
                Vector3(0.0)),
            components.CameraComponent.orthographic(
                Rectangle(
                    0.0,
                    0.0,
                    renderer.get_framebuffer_width() / renderer.get_framebuffer_height(),
                    1.0),
                z_clip=(0.001, 10.0)))

        self._scene.set_current_camera_entity(camera_entity)

    def on_close(self) -> None:
        imgui_renderer.shutdown()

    @debug.profiled('editor')
    def on_update(self, frametime: float) -> None:
        self._update_scene()
        imgui.get_io().delta_time = frametime

    @debug.profiled('editor')
    def on_render(self, frametime: float) -> None:
        self._render_scene(renderer.get_framebuffer_width(), renderer.get_framebuffer_height())
        self._render_imgui(window.get_framebuffer_width(), window.get_framebuffer_height())

    @debug.profiled('editor', 'update')
    def _update_scene(self) -> None:
        for transform in self._scene.get_component(components.TransformComponent):
            if transform.needs_recalculate:
                transform.recalculate()

        for camera in self._scene.get_component(components.CameraComponent):
            if camera.needs_recalculate:
                camera.recalculate()

    @debug.profiled('editor', 'render')
    def _render_scene(self, fb_width: int, fb_height: int) -> None:
        commands.scissor(0, 0, fb_width, fb_height)

        renderer.begin_frame(renderer.DEFERRED_PIPELINE)
        renderer.set_camera_transform(*self._get_scene_camera_matrices())

        for _, (transform, sprite) in self._scene.get_components(components.TransformComponent, components.SpriteComponent):
            image = assets.get_or_empty(Image, sprite.image_id)
            model = assets.get_or_empty(Model, sprite.model_id)

            renderer.render(
                model,
                transform.matrix,
                sprite.color,
                image.texture)

        renderer.end_frame()

    @debug.profiled('editor', 'render')
    def _render_imgui(self, fb_width: int, fb_height: int) -> None:
        imgui.new_frame()

        _enable_dockspace('main')

        self._draw_scene_preview()
        self._draw_renderer_info()
        self._draw_assets_panel()
        self._draw_scene_hierarchy_tree()
        self._draw_inspector()

        imgui.render()

        commands.scissor(0, 0, fb_width, fb_height)
        commands.clear_color(*self._framebuffer_clear_color)
        rendering.clear(rendering.ClearMask.COLOR_BUFFER_BIT)
        imgui_renderer.render(imgui.get_draw_data())

    @debug.profiled('editor', 'update')
    def _draw_assets_panel(self) -> None:
        with imgui.begin('Assets'):
            pass

    @debug.profiled('editor', 'update')
    def _draw_renderer_info(self) -> None:
        with imgui.begin('Renderer'):
            imgui.text_unformatted(f'Framebuffer size: {renderer.get_framebuffer_width()}x{renderer.get_framebuffer_height()}')
            imgui.text_unformatted(f'Window size: {window.get_width()}x{window.get_height()}')
            imgui.text_unformatted(f'Frametime: {(self.frametime * 1000.0):.2f} ms')
            imgui.text_unformatted(f'FPS: {(1.0 / self.frametime):.1f}')
            imgui.separator()

            clear_color_changed, new_clear_color  = imgui.color_edit4(
                'Clear color',
                *renderer.get_clear_color(),
                imgui.COLOR_EDIT_NO_PICKER | imgui.COLOR_EDIT_NO_SIDE_PREVIEW)
            if clear_color_changed:
                renderer.set_clear_color(Vector4(*new_clear_color))

    @debug.profiled('editor', 'imgui')
    def _draw_scene_preview(self) -> None:
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0, 0))

        with imgui.begin(self._scene.name):
            imgui.pop_style_var(1)

            content_region = imgui.get_content_region_available()
            content_width = int(content_region.x)
            content_height = int(content_region.y)

            self._resize_scene_camera(content_width, content_height)

            imgui.image(renderer.get_framebuffer_color_texture_id(), content_region.x, content_region.y)

    @debug.profiled('editor', 'imgui')
    def _draw_scene_hierarchy_tree(self) -> None:
        with imgui.begin('Scene'):
            for entity in self._scene.get_entities():
                entity_components = self._scene.get_components_for_entity(entity)
                if imgui.tree_node(_get_entity_name(entity, entity_components), imgui.TREE_NODE_DEFAULT_OPEN):
                    for component in entity_components:
                        imgui.tree_node(type(component).__name__, imgui.TREE_NODE_LEAF | imgui.TREE_NODE_NO_TREE_PUSH_ON_OPEN)

                        if imgui.is_item_clicked():
                            self._inspector_window.set_selected_item(component)

                    imgui.tree_pop()

    @debug.profiled('editor', 'imgui')
    def _draw_inspector(self) -> None:
        self._inspector_window.render()

    def _resize_scene_camera(self, content_width: int, content_height: int) -> None:
        camera_entity = self._scene.get_current_camera_entity()
        if camera_entity != -1:
            camera = self._scene.get_component_for_entity(camera_entity, components.CameraComponent)
            aspect = content_width / content_height
            camera.viewport = Rectangle(0.0, 0.0, aspect, 1.0)
            camera.aspect = aspect

    def _get_scene_camera_matrices(self) -> tuple[Matrix4, Matrix4]:
        camera_entity = self._scene.get_current_camera_entity()
        if camera_entity != -1:
            camera = self._scene.get_component_for_entity(camera_entity, components.CameraComponent)
            transform = self._scene.get_component_for_entity(camera_entity, components.TransformComponent)

            return (transform.matrix, camera.projection)

        return (Matrix4.identity(), Matrix4.identity())

def _get_entity_name(entity: int, entity_components: t.Iterable[ecs.Component]) -> str:
    for comp in entity_components:
        if isinstance(comp, components.TagComponent):
            return comp.name

    return str(entity)

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

@debug.profiled('editor', 'imgui')
def _initialize_imgui() -> None:
    imgui.create_context()
    imgui.style_colors_dark()

    io = imgui.get_io()
    io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
    io.display_size = (window.get_framebuffer_width(), window.get_framebuffer_height())
    io.key_map[imgui.KEY_TAB] = Key.Tab
    io.key_map[imgui.KEY_LEFT_ARROW] = Key.Left
    io.key_map[imgui.KEY_RIGHT_ARROW] = Key.Right
    io.key_map[imgui.KEY_UP_ARROW] = Key.Up
    io.key_map[imgui.KEY_DOWN_ARROW] = Key.Down
    io.key_map[imgui.KEY_PAGE_UP] = Key.PageUp
    io.key_map[imgui.KEY_PAGE_DOWN] = Key.PageDown
    io.key_map[imgui.KEY_HOME] = Key.Home
    io.key_map[imgui.KEY_END] = Key.End
    io.key_map[imgui.KEY_INSERT] = Key.Insert
    io.key_map[imgui.KEY_DELETE] = Key.Delete
    io.key_map[imgui.KEY_BACKSPACE] = Key.Backspace
    io.key_map[imgui.KEY_SPACE] = Key.Space
    io.key_map[imgui.KEY_ENTER] = Key.Enter
    io.key_map[imgui.KEY_ESCAPE] = Key.Escape
    io.key_map[imgui.KEY_PAD_ENTER] = Key.KeypadEnter
    io.key_map[imgui.KEY_A] = Key.A
    io.key_map[imgui.KEY_C] = Key.C
    io.key_map[imgui.KEY_V] = Key.V
    io.key_map[imgui.KEY_X] = Key.X
    io.key_map[imgui.KEY_Y] = Key.Y
    io.key_map[imgui.KEY_Z] = Key.Z

    events.register(_imgui_key_down_callback, events.KeyDownEvent, priority=1)
    events.register(_imgui_key_up_callback, events.KeyUpEvent, priority=1)
    events.register(_imgui_resize_callback, events.ResizeEvent, priority=1)
    events.register(_imgui_mouse_callback, events.MouseMoveEvent, priority=1)
    events.register(_imgui_mouse_button_down_callback, events.MouseButtonDownEvent, priority=1)
    events.register(_imgui_mouse_button_up_callback, events.MouseButtonUpEvent, priority=1)
    events.register(_imgui_scroll_callback, events.MouseScrollEvent, priority=1)
    events.register(_imgui_char_event, events.CharEvent, priority=1)

def _imgui_char_event(event: events.CharEvent) -> None:
    io = imgui.get_io()
    io.add_input_character(event.character)

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

def _imgui_update_key_mods(mods: KeyMod) -> None:
    io = imgui.get_io()

    io.key_ctrl = KeyMod.Control in mods
    io.key_alt = KeyMod.Alt in mods
    io.key_shift = KeyMod.Shift in mods
    io.key_super = KeyMod.Super in mods

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

def _compute_fb_scale(window_width: int, window_height: int, fb_width: int, fb_height: int) -> tuple[float, float]:
    if window_width != 0 and window_height != 0:
        return (fb_width / window_width, fb_height / window_height)

    return (1.0, 1.0)

def _create_quad_model() -> Model:
    model = Model(AssetSource(''), uuid.uuid4(), True)
    model._vertex_data = np.array([
        0.0, 0.0, 0.0,  0.0, 0.0,  0.0, 0.0, 1.0,
        1.0, 0.0, 0.0,  1.0, 0.0,  0.0, 0.0, 1.0,
        1.0, 1.0, 0.0,  1.0, 1.0,  0.0, 0.0, 1.0,
        0.0, 1.0, 0.0,  0.0, 1.0,  0.0, 0.0, 1.0],
        dtype=np.float32)
    model._index_data = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint8)
    model._vertex_count = 4
    model._index_count = 6
    model._elements_type = ElementsType.UNSIGNED_BYTE

    return model

def _create_cube_model() -> Model:
    model = Model(AssetSource(''), uuid.uuid4(), True)
    model._vertex_data = np.array([
        0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
        1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0,
        0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0,

        1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0,
        0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0,
        0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, -1.0,
        1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, -1.0,

        0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 1.0, 0.0, -1.0, 0.0, 0.0,
        0.0, 1.0, 1.0, 1.0, 1.0, -1.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0,

        1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
        1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0,
        1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0,
        1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0,

        0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
        1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0,
        1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0,
        0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0,

        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0,
        1.0, 0.0, 0.0, 1.0, 0.0, 0.0, -1.0, 0.0,
        1.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, 0.0,
        0.0, 0.0, 1.0, 0.0, 1.0, 0.0, -1.0, 0.0],
        dtype=np.float32)
    model._index_data = np.array([
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        8, 9, 10, 10, 11, 8,
        12, 13, 14, 14, 15, 12,
        16, 17, 18, 18, 19, 16,
        20, 21, 22, 22, 23, 20],
        dtype=np.uint8)
    model._vertex_count = 24
    model._index_count = 36
    model._elements_type = ElementsType.UNSIGNED_BYTE

    return model

def _create_empty_image() -> Image:
    empty_image = Image(AssetSource(''), uuid.uuid4(), True)
    empty_image._texture = renderer.get_white_texture()

    return empty_image

def _create_empty_model() -> Model:
    empty_model = Model(AssetSource(''), uuid.uuid4(), True)
    empty_model._vertex_data = np.empty((0, ), dtype=np.float32)
    empty_model._index_data = np.empty((0, ), dtype=np.uint8)
    empty_model._vertex_count = 0
    empty_model._index_count = 0
    empty_model._elements_type = ElementsType.UNSIGNED_BYTE

    return empty_model

def _initialize_assets() -> None:
    empty_image = _create_empty_image()
    Image.register_empty_asset(empty_image)
    assets.add_asset(empty_image)

    empty_model = _create_empty_model()
    Model.register_empty_asset(empty_model)
    assets.add_asset(empty_model)

    Image.register_loader(StandardImageLoader())
    Image.register_loader(DDSLoader())

if __name__ == '__main__':
    app = EditorApplication()
    app.run()
