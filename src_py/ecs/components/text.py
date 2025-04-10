import dataclasses
from uuid import UUID

from spyke import math
from spyke.ecs.components.component import Component


@dataclasses.dataclass
class TextComponent(Component):
    text: str
    size: int
    color: math.Vector4
    font_id: UUID
