from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.resources import Image
    from typing import Optional
    from weakref import ProxyType
    ImageProxy = ProxyType[Image]

import glm
import uuid
from spyke import resources
from .component import Component


class SpriteComponent(Component):
    __slots__ = (
        '__weakref__',
        'image',
        'tiling_factor',
        'color'
    )

    def __init__(self, image_id: Optional[uuid.UUID], tiling_factor: glm.vec2, color: glm.vec4):
        self.image: Optional[ImageProxy] = resources.get(
            image_id) if image_id else None
        self.tiling_factor: glm.vec2 = tiling_factor
        self.color: glm.vec4 = color
