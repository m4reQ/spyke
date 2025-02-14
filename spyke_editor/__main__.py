import uuid

import numpy as np
from pygl import commands
from pygl.math import Matrix4, Vector3, Vector4, deg_to_rad
from pygl.rendering import ElementsType
from pygl.textures import (InternalFormat, MagFilter, MinFilter, PixelFormat,
                           Texture, TextureSpec, TextureTarget, UploadInfo)

from spyke import application, assets, debug
from spyke.assets import (AssetConfig, Image, ImageConfig, ImageLoadData,
                          Model, ModelLoadData)
from spyke.assets.loaders import DDSLoader, StandardImageLoader
from spyke.debug import profiling
from spyke.ecs import Scene, SpriteComponent, TagComponent, TransformComponent
from spyke.graphics import camera, renderer, window
from spyke.math import Viewport3D
from spyke_editor import imgui_renderer, ui


class EditorApplication(application.Application):
    def __init__(self) -> None:
        super().__init__(window.WindowSettings(1080, 720, 'Spyke Editor', window.WindowFlags.RESIZABLE | window.WindowFlags.ENABLE_VSYNC))

        self._framebuffer_clear_color = Vector4(0.0, 0.0, 0.0, 1.0)
        self._scene = _create_default_editor_scene()
        self._image1: uuid.UUID
        self._image2: uuid.UUID
        self._image3: uuid.UUID
        self._image4: uuid.UUID

        # default editor resources
        self._quad_model: uuid.UUID
        self._cube_model: uuid.UUID

    @debug.profiled
    def on_load(self) -> None:
        _initialize_assets()

        ui.initialize(self._scene)
        ui.clear_color_changed().subscribe(lambda color: setattr(self, '_framebuffer_clear_color', color))

        image_config = ImageConfig.default()
        image_config.mipmap_count = 2

        self._image1 = assets.load_from_file(Image, r'C:\Users\mmize\Pictures\unnamedfff.png', image_config)
        self._image2 = assets.load_from_file(Image, r'C:\Users\mmize\Pictures\unnamed (1).png', image_config)
        self._image3 = assets.load_from_file(Image, r'C:\Users\mmize\Pictures\o.dds', image_config)
        self._image4 = assets.load_from_file(Image, r'C:\Users\mmize\Pictures\1.png', image_config)
        self._quad_model = _create_quad_model()
        self._cube_model = _create_cube_model()

        self._scene.create_entity(
            TagComponent('C U B E'),
            SpriteComponent(Vector4(1.0), self._cube_model, self._image4),
            TransformComponent(
                Vector3(0.0, 0.0, 0.0),
                Vector3(0.2),
                Vector3(0.0)))

        self._scene.create_entity(
            TagComponent('Surface plane'),
            SpriteComponent(Vector4(0.2, 0.45, 0.6, 1.0), self._quad_model, Image.get_empty_asset()),
            TransformComponent(
                Vector3(-2.0, -0.5, -4.0),
                Vector3(5.0, 5.0, 0.0),
                Vector3(0.0, 0.0, 0.0)))

    def on_close(self) -> None:
        imgui_renderer.shutdown()

    @debug.profiled
    def on_update(self, frametime: float) -> None:
        self._update_scene()
        ui.update(frametime)

    @debug.profiled
    def on_render(self, frametime: float) -> None:
        self._render_scene(*window.get_size())
        ui.render()

    @debug.profiled
    def _update_scene(self) -> None:
        for transform in self._scene.get_component(TransformComponent):
            if transform.needs_recalculate:
                transform.recalculate()

    @debug.profiled
    def _render_scene(self, fb_width: int, fb_height: int) -> None:
        commands.scissor(0, 0, fb_width, fb_height)

        renderer.begin_frame(renderer.DEFERRED_PIPELINE)
        renderer.set_clear_color(self._framebuffer_clear_color)
        renderer.set_camera_transform(
            Matrix4.look_at(Vector3(0.0, 0.0, 3.0), Vector3.zero()),
            self._scene.camera.projection)

        for _, (transform, sprite) in self._scene.get_components(TransformComponent, SpriteComponent):
            model = assets.get_or_empty(Model, sprite.model_id)
            if not model.is_loaded:
                continue

            renderer.render(
                model,
                transform.matrix,
                sprite.color,
                _get_sprite_texture(sprite))

        renderer.end_frame()

def _get_sprite_texture(sprite: SpriteComponent) -> Texture | None:
    if sprite.image_id is not None:
        image = assets.get(Image, sprite.image_id)
        if image.is_loaded:
            return image.texture

    return None

def _create_quad_model() -> uuid.UUID:
    data = ModelLoadData(
        np.array([0, 1, 2, 2, 3, 0], dtype=np.uint8),
        6,
        np.array([
            0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
            1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0,
            1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            dtype=np.float32),
        4,
        ElementsType.UNSIGNED_BYTE)

    return assets.load_from_data(Model, data, AssetConfig.default())

def _create_cube_model() -> uuid.UUID:
    data = ModelLoadData(
        np.array([
            0, 1, 2, 2, 3, 0,
            4, 5, 6, 6, 7, 4,
            8, 9, 10, 10, 11, 8,
            12, 13, 14, 14, 15, 12,
            16, 17, 18, 18, 19, 16,
            20, 21, 22, 22, 23, 20],
            dtype=np.uint8),
        36,
        np.array([
            # front face
            0.0, 0.0, 0.0,  0.0, 0.0,  0.0, 0.0, 0.0,
            0.0, 1.0, 0.0,  1.0, 0.0,  0.0, 0.0, 0.0,
            1.0, 1.0, 0.0,  1.0, 1.0,  0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,  0.0, 1.0,  0.0, 0.0, 0.0,

            # left face
            0.0, 0.0, 1.0,  0.0, 0.0,  0.0, 0.0, -1.0,
            0.0, 1.0, 1.0,  1.0, 0.0,  0.0, 0.0, -1.0,
            0.0, 1.0, 0.0,  1.0, 1.0,  0.0, 0.0, -1.0,
            0.0, 0.0, 0.0,  0.0, 1.0,  0.0, 0.0, -1.0,

            # top face
            0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0,
            0.0, 1.0, 1.0, 1.0, 0.0, -1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 0.0, 0.0,
            1.0, 1.0, 0.0, 0.0, 1.0, -1.0, 0.0, 0.0,

            # right face
            1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0,
            1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0,

            # back face
            1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0,

            # bottom face
            0.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0, 0.0, -1.0, 0.0,
            1.0, 0.0, 0.0, 1.0, 1.0, 0.0, -1.0, 0.0,
            1.0, 0.0, 1.0, 0.0, 1.0, 0.0, -1.0, 0.0],
            dtype=np.float32),
        24,
        ElementsType.UNSIGNED_BYTE)

    return assets.load_from_data(Model, data, AssetConfig.default())

def _create_empty_model() -> uuid.UUID:
    data = ModelLoadData(
        np.empty((0, ), dtype=np.uint8),
        0,
        np.empty((0, ), dtype=np.float32),
        0,
        ElementsType.UNSIGNED_BYTE)

    return assets.load_from_data(Model, data, AssetConfig.default())

def _create_empty_image() -> uuid.UUID:
    data = ImageLoadData(
        TextureSpec(
            TextureTarget.TEXTURE_2D,
            1,
            1,
            InternalFormat.RGBA8,
            min_filter=MinFilter.NEAREST,
            mag_filter=MagFilter.NEAREST),
        [UploadInfo(PixelFormat.RGBA, 1, 1, generate_mipmap=False)],
        np.array([255, 255, 255, 255], dtype=np.uint8))

    return assets.load_from_data(Image, data, ImageConfig.default())

def _initialize_assets() -> None:
    Image.register_loader(StandardImageLoader())
    Image.register_loader(DDSLoader())

    empty_image = assets.get(Image, _create_empty_image())
    Image.register_empty_asset(empty_image)
    assets.add_asset(empty_image)

    # empty_model = assets.get(Model, _create_empty_model())
    # Model.register_empty_asset(empty_model)
    # assets.add_asset(empty_model)

def _create_default_editor_scene() -> Scene:
    return Scene(
        'editor-main-scene',
        camera.PerspectiveCamera(
            Viewport3D(0.0, 1.0, 0.0, 1.0, 0.001, 10.0),
            deg_to_rad(45.0),
            1.0))

if __name__ == '__main__':
    profiling.begin_profiling_session('./spyke_profile.json')

    app = EditorApplication()
    app.run()

    profiling.end_profiling_session()
