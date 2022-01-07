from .rendering import renderer as Renderer
from .cameras import *
from .windowSpecs import WindowSpecs

import glm


def Color(r: float, g: float, b: float, a: float) -> glm.vec4:
    return glm.vec4(r, g, b, a)


def ColorByte(r: int, g: int, b: int, a: int) -> glm.vec4:
    return glm.vec4(r / 255.0, g / 255.0, b / 255.0, a / 255.0)
