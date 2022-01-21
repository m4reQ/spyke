import glm
from .windowSpecs import WindowSpecs
from .rectangle import Rectangle

__all__ = [
    'WindowSpecs',
    'Rectangle',
    'color'
]


def color(r: float, g: float, b: float, a: float) -> glm.vec4:
    return glm.vec4(r, g, b, a)
