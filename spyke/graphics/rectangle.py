import dataclasses

import glm
import numpy as np

@dataclasses.dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float
    
    def to_coordinates(self) -> np.ndarray:
        #0.0, 1.0,
            # 1.0, 1.0,
            # 1.0, 0.0,
            # 1.0, 0.0,
            # 0.0, 0.0,
            # 0.0, 1.0
        return np.array([
            self.left, self.top,
            self.right, self.top,
            self.right, self.bottom,
            self.right, self.bottom,
            self.left, self.bottom,
            self.left, self.top], dtype=np.float32)

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
    def one(cls):
        return Rectangle(0.0, 0.0, 1.0, 1.0)
