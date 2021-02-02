from .texturing import *
from .rendering.renderer import Renderer
from .rendering.renderStats import RenderStats
from .rendering.rendererSettings import RendererSettings
from .shader import Shader
from .text.font import Font
from .glCommands import GLCommand
from .cameras import *
from .vertexArray import VertexArray
from .buffers import *

from glm import vec4 as __Color

def Color(r: float, g: float, b: float, a: float) -> __Color:
    return __Color(r, g, b, a)

def ColorRGBA(r: int, g: int, b: int, a: int) -> __Color:
    return __Color(r / 255.0, g / 255.0, b / 255.0, a / 255.0)