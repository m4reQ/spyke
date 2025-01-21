import dataclasses

from pygl.math import Matrix4, Quaternion, Vector3
from spyke.ecs import Component


@dataclasses.dataclass(repr=False, slots=True, eq=False)
class TransformComponent(Component):
    matrix: Matrix4
    _position: Vector3
    _scale: Vector3
    _rotation: Quaternion

    def __init__(self,
                 position: Vector3,
                 scale: Vector3,
                 rotation: Vector3):
        self._position = position
        self._scale = scale
        self._rotation_hint = rotation
        self._rotation = Quaternion.from_euler_deg(rotation)
        self._needs_recalculate = True

        self.matrix: Matrix4

        self.recalculate()

    def recalculate(self) -> None:
        self.matrix = Matrix4.transform(self._position, self._scale, self._rotation)
        self._needs_recalculate = False

    @property
    def needs_recalculate(self) -> bool:
        return self._needs_recalculate

    @property
    def position(self) -> Vector3:
        return self._position

    @position.setter
    def position(self, value: Vector3) -> None:
        self._position = value
        self._needs_recalculate = True

    @property
    def scale(self) -> Vector3:
        return self._scale

    @scale.setter
    def scale(self, value: Vector3) -> None:
        self._scale = value
        self._needs_recalculate = True

    @property
    def rotation(self) -> Vector3:
        return self._rotation_hint

    @rotation.setter
    def rotation(self, value: Vector3):
        self._rotation_hint = value % 360.0
        self._rotation = Quaternion.from_euler_deg(value)
        self._needs_recalculate = True
