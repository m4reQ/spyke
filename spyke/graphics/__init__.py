from .rendering import renderer as Renderer
from .rendering.renderStats import RenderStats
from .shader import Shader
from .vertexArray import VertexArray
from .text.font import Font
from .contextInfo import ContextInfo
from .texturing import *
from .gl import *
from .cameras import *

from glm import vec4 as __Color

def Color(r: float, g: float, b: float, a: float) -> __Color:
    return __Color(r, g, b, a)

def ColorRGBA(r: int, g: int, b: int, a: int) -> __Color:
    return __Color(r / 255.0, g / 255.0, b / 255.0, a / 255.0)