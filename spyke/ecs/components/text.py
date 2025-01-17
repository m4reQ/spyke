import dataclasses
from uuid import UUID

from pygl.math import Vector4

from spyke.ecs import Component


@dataclasses.dataclass
class TextComponent(Component):
    text: str
    size: int
    color: Vector4
    font_id: UUID
