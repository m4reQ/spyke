from __future__ import annotations
import glm
from dataclasses import dataclass


@dataclass
class Rectangle:
    __slots__ = (
        '__weakref__',
        'x',
        'y',
        'width',
        'height'
    )

    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def top(self) -> float:
        return self.y

    @property
    def size(self) -> glm.vec2:
        return glm.vec2(self.width, self.height)

    @property
    def origin(self) -> glm.vec2:
        return glm.vec2(self.x, self.y)

    @classmethod
    def one(cls) -> Rectangle:
        return Rectangle(0.0, 0.0, 1.0, 1.0)
