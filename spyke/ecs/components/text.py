from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Optional
    from weakref import ProxyType
    from spyke.resources import Font
    FontProxy = ProxyType[Font]

import glm
import uuid
from spyke import resources


class TextComponent:
    __slots__ = (
        '__weakref__',
        'text',
        'size',
        'color',
        'font',
    )

    def __init__(self, text: str, size: int, font_id: uuid.UUID, color: glm.vec4):
        self.text: str = text
        self.size: int = size
        self.color: glm.vec4 = color
        self.font: Optional[FontProxy] = resources.get(font_id)
