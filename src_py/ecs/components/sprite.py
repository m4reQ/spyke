import dataclasses
from uuid import UUID

from spyke import assets, math
from spyke.ecs.components.component import Component
from spyke.graphics import gl


@dataclasses.dataclass(eq=False, slots=True)
class SpriteComponent(Component):
    color: math.Vector4
    model_id: UUID
    albedo_id: UUID
    specular_id: UUID | None = None

    @property
    def albedo_texture(self) -> gl.Texture | None:
        if self.albedo_id is not None:
            image = assets.get(assets.Image, self.albedo_id)
            if image.is_loaded:
                return image.texture

        return None

    @property
    def specular_texture(self) -> gl.Texture | None:
        if self.specular_id is not None:
            image = assets.get(assets.Image, self.specular_id)
            if image.is_loaded:
                return image.texture

        return None
