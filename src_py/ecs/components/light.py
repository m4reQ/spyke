import dataclasses

from spyke import math
from spyke.ecs.components.component import Component


@dataclasses.dataclass(eq=False, slots=True)
class LightComponent(Component):
    color: math.Vector3
    intensity: float
