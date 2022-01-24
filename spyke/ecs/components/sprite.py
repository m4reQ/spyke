from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.resources import Image

import glm
import uuid
from spyke import resources


class SpriteComponent:
    __slots__ = (
        '__weakref__',
        'image',
        'tiling_factor',
        'color'
    )

    def __init__(self, image_id: uuid.UUID, tiling_factor: glm.vec2, color: glm.vec4):
        self.image: Image = resources.get(image_id)
        self.tiling_factor: glm.vec2 = tiling_factor
        self.color: glm.vec4 = color
