from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.graphics.rectangle import Rectangle
    from typing import Optional, Tuple
    ClipSpace = Tuple[float, float]

from .component import Component
from spyke.enums import CameraType
from spyke.exceptions import SpykeException
import glm


class CameraComponent(Component):
    __slots__ = (
        '__weakref__',
        'is_primary',
        'type',
        'viewport',
        'clipping',
        'fov',
        'aspect',
        'projection',
        'view',
        '_should_recalculate'
    )

    @classmethod
    def orthographic(cls, viewport: Rectangle, *, clipping: Optional[ClipSpace] = None, is_primary: bool = False):
        return cls(CameraType.Orthographic, viewport, clipping=clipping, is_primary=is_primary)

    @classmethod
    def perspective(cls, viewport: Rectangle, *, fov: float = 1.0, aspect: float = 1.0, is_primary: bool = False):
        return cls(CameraType.Perspective, viewport, fov=fov, aspect=aspect, is_primary=is_primary)

    def __init__(self, _type: CameraType, viewport: Rectangle, *, fov: float = 1.0, aspect: float = 1.0, clipping: Optional[ClipSpace] = None, is_primary: bool = False):
        if clipping and not len(clipping) == 2:
            raise SpykeException(
                'Tuple passed for "clipping" parameter must be the length of 2.')

        self.is_primary: bool = is_primary
        self.type: CameraType = _type
        self.viewport: Rectangle = viewport
        self.clipping: ClipSpace = clipping or (-1.0, 10.0)
        self.fov: float = fov
        self.aspect: float = aspect

        self.projection: glm.mat4 = glm.mat4(1.0)
        self.view: glm.mat4 = glm.mat4(1.0)

        self._should_recalculate: bool = False

    def recalculate(self, transform: glm.mat4) -> None:
        self._should_recalculate = False

        self.view = glm.inverse(transform)

        if self.type == CameraType.Orthographic:
            self.projection = glm.ortho(*tuple(self.viewport), *self.clipping)
        elif self.type == CameraType.Perspective:
            self.projection = glm.perspective(
                self.fov, self.aspect, *self.clipping)

    @property
    def should_recalculate(self) -> bool:
        return self._should_recalculate

    @property
    def view_projection(self) -> glm.mat4:
        # TODO: Check if the multiplication order is correct
        return self.projection * self.view
