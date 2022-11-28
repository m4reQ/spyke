import dataclasses
from uuid import UUID

import glm

from spyke.ecs import Component


@dataclasses.dataclass
class SpriteComponent(Component):
    color: glm.vec4
    image_id: UUID
    tiling_factor: glm.vec2
