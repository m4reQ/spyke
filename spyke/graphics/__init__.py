import OpenGL

OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True
OpenGL.ERROR_CHECKING = __debug__
OpenGL.ERROR_ON_COPY = False

from .rectangle import Rectangle
from .rendering import renderer

__all__ = [
    'Rectangle',
    'renderer'
]
