from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.graphics.rectangle import Rectangle
    import glm


class Glyph:
    __slots__ = (
        'tex_rect',
        'size',
        'bearing',
        'advance'
    )

    def __init__(self, size: glm.ivec, bearing: glm.ivec2, advance: int, tex_rect: Rectangle):
        self.tex_rect: Rectangle = tex_rect
        self.size: glm.ivec2 = size
        self.bearing: glm.ivec2 = bearing
        self.advance: int = advance
