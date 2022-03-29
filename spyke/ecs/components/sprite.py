from __future__ import annotations
from spyke import resources
from spyke.resources import Image
from .component import Component
from typing import Optional
import glm
import uuid


class SpriteComponent(Component):
    __slots__ = (
        '__weakref__',
        'image',
        'tiling_factor',
        'color'
    )

    def __init__(self, image_id: Optional[uuid.UUID], tiling_factor: glm.vec2, color: glm.vec4):
        self.image: Optional[Image]
        self.tiling_factor: glm.vec2 = tiling_factor
        self.color: glm.vec4 = color

        _image = resources.get(image_id) if image_id else None
        assert isinstance(_image, Image) or _image is None, f'UUID: {image_id} points to a resource of type: {type(_image)}. Expected type: {Image.__name__}.'
        self.image = _image
