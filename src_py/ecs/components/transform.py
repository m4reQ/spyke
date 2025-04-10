import dataclasses

from spyke import math
from spyke.ecs.components.component import Component


@dataclasses.dataclass(repr=False, slots=True, eq=False)
class TransformComponent(Component):
    matrix: math.Matrix4
    _position: math.Vector3
    _scale: math.Vector3
    _rotation: math.Vector3 # TODO Use quaternions for rotation once they are implemented
    _rotation_hint: math.Vector3 = dataclasses.field(init=False)
    _needs_recalculate: bool = dataclasses.field(init=False)

    def __init__(self,
                 position: math.Vector3,
                 scale: math.Vector3,
                 rotation: math.Vector3) -> None:
        self._position = position
        self._scale = scale
        self._rotation_hint = rotation
        self._rotation = rotation
        self._needs_recalculate = True

        self.recalculate()

    def recalculate(self) -> None:
        self.matrix = math.Matrix4.transform(self._position, self._scale, self._rotation)
        self._needs_recalculate = False

    @property
    def needs_recalculate(self) -> bool:
        return self._needs_recalculate

    @property
    def position(self) -> math.Vector3:
        return self._position

    @position.setter
    def position(self, value: math.Vector3) -> None:
        self._position = value
        self._needs_recalculate = True

    @property
    def scale(self) -> math.Vector3:
        return self._scale

    @scale.setter
    def scale(self, value: math.Vector3) -> None:
        self._scale = value
        self._needs_recalculate = True

    @property
    def rotation(self) -> math.Vector3:
        return self._rotation_hint

    @rotation.setter
    def rotation(self, value: math.Vector3):
        self._rotation_hint = value % 360.0
        self._rotation = value
        self._needs_recalculate = True
