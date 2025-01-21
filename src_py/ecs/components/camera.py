import dataclasses
import enum
import typing as t

from pygl.math import Matrix4
from spyke.ecs import Component
from spyke.graphics.rectangle import Rectangle

_DEFAULT_Z_CLIP = (-1.0, 100.0)

class CameraType(enum.Enum):
    ORTHO = enum.auto()
    PERSPECTIVE = enum.auto()

@dataclasses.dataclass(slots=True, eq=False)
class CameraComponent(Component):
    type: CameraType
    _viewport: Rectangle
    _z_clip: tuple[float, float]
    _fov: float = 0.0
    _aspect: float = 0.0

    projection: Matrix4 = dataclasses.field(init=False, default_factory=Matrix4.identity)
    _needs_recalculate: bool = dataclasses.field(init=False, default=True)

    @classmethod
    def orthographic(cls,
                     viewport: Rectangle,
                     z_clip: tuple[float, float] = _DEFAULT_Z_CLIP) -> t.Self:
        return cls(
            CameraType.ORTHO,
            viewport,
            z_clip)

    @classmethod
    def perspective(cls,
                    viewport: Rectangle,
                    z_clip: tuple[float, float] = _DEFAULT_Z_CLIP,
                    fov: float = 1.0,
                    aspect: float = 1.0):
        return cls(
            CameraType.PERSPECTIVE,
            viewport,
            z_clip,
            fov,
            aspect)

    def recalculate(self) -> None:
        if self.type == CameraType.ORTHO:
            self.projection = Matrix4.ortho(
                self.viewport.left,
                self.viewport.right,
                self.viewport.bottom,
                self.viewport.top,
                self.z_clip[0],
                self.z_clip[1])
        elif self.type == CameraType.PERSPECTIVE:
            self.projection = Matrix4.perspective(
                self.fov,
                self.aspect,
                self.z_clip[0],
                self.z_clip[1])

        self._needs_recalculate = False

    @property
    def needs_recalculate(self) -> bool:
        return self._needs_recalculate

    @property
    def viewport(self) -> Rectangle:
        return self._viewport

    @viewport.setter
    def viewport(self, value: Rectangle) -> None:
        self._viewport = value
        self._needs_recalculate = True

    @property
    def z_clip(self) -> tuple[float, float]:
        return self._z_clip

    @z_clip.setter
    def z_clip(self, value: tuple[float, float]) -> None:
        self._z_clip = value
        self._needs_recalculate = True

    @property
    def fov(self) -> float:
        return self._fov

    @fov.setter
    def fov(self, value: float) -> None:
        self._fov = value
        self._needs_recalculate = True

    @property
    def aspect(self) -> float:
        return self._aspect

    @aspect.setter
    def aspect(self, value: float) -> None:
        self._aspect = value
        self._needs_recalculate = True
