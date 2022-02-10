import glm
from .rectangle import Rectangle
from .glyph import Glyph
from .texturing import Texture, TextureSpec

__all__ = [
    'Rectangle',
    'color'
]


def color(r: float, g: float, b: float, a: float) -> glm.vec4:
    return glm.vec4(r, g, b, a)
