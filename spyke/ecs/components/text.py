from __future__ import annotations

import glm
import uuid
from spyke import resources
from spyke.resources import Font
from spyke.exceptions import SpykeException


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
        self.font: Font

        _font = resources.get(font_id)
        if not isinstance(_font, Font):
            raise SpykeException(
                f'UUID: {font_id} points to a resource of type: {type(_font)}. Expected type: {Font.__name__}.')

        self.font = _font
