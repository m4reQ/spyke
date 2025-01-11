from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float

    def to_int(self) -> RectangleInt:
        return RectangleInt(int(self.x), int(self.y), int(self.width), int(self.height))

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

@dataclasses.dataclass
class RectangleInt:
    x: int
    y: int
    width: int
    height: int

    @property
    def left(self) -> int:
        return self.x

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    @property
    def top(self) -> int:
        return self.y
