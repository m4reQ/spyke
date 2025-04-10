import dataclasses

from spyke import math


@dataclasses.dataclass(slots=True)
class LightData:
    position: math.Vector3
    color: math.Vector3
    intensity: float
