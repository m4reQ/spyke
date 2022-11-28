import dataclasses
from uuid import UUID

import glm

from spyke.ecs import Component


@dataclasses.dataclass
class TextComponent(Component):
    text: str
    size: int
    color: glm.vec4
    font_id: UUID
