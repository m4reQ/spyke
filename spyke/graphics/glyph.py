from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.graphics.rectangle import Rectangle
    import glm

from dataclasses import dataclass


@dataclass
class Glyph:
    __slots__ = (
        'tex_rect',
        'size',
        'bearing',
        'advance'
    )

    size: glm.ivec2
    bearing: glm.ivec2
    advance: int
    tex_rect: Rectangle
