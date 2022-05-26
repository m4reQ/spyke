import dataclasses

import glm

from spyke.graphics.rectangle import Rectangle

@dataclasses.dataclass
class Glyph:
    __slots__ = (
        '__weakref__',
        'tex_rect',
        'size',
        'bearing',
        'advance'
    )

    size: glm.ivec2
    bearing: glm.ivec2
    advance: int
    tex_rect: Rectangle
