import imgui

from pygl.textures import Texture
from spyke import assets
from spyke.ecs import SpriteComponent
from spyke.graphics import renderer
from spyke_editor.ui.inspector import Inspector
from pygl.math import Vector4


class SpriteComponentInspector(Inspector[SpriteComponent]):
    def get_supported_types(self) -> tuple[type]:
        return (SpriteComponent,)

    def render(self, item: SpriteComponent) -> None:
        color_changed, new_color = imgui.color_edit4(
            'Color',
            *item.color,
            imgui.COLOR_EDIT_NONE)
        if color_changed:
            item.color = Vector4(*new_color)

        imgui.text_unformatted('Texture')

        texture: Texture
        if item.image_id is None:
            texture = renderer.get_white_texture()
        else:
            image = assets.get_or_empty(assets.Image, item.image_id)
            if image.is_loaded:
                texture = image.texture
            else:
                texture = renderer.get_white_texture()

        img_width, img_height = imgui.get_content_region_available()
        imgui.image(
            texture.id,
            img_width,
            min(img_width, img_height))
