import dataclasses
from uuid import UUID

from pygl.math import Vector4

from spyke.ecs.components.component import Component


@dataclasses.dataclass(eq=False, slots=True)
class SpriteComponent(Component):
    color: Vector4
    model_id: UUID
    image_id: UUID
