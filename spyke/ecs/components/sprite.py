from __future__ import annotations
import typing

from spyke.exceptions import SpykeException
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
        self.image: Optional[ImageProxy]
        self.tiling_factor: glm.vec2 = tiling_factor
        self.color: glm.vec4 = color

        _image = resources.get(image_id) if image_id else None
        if _image is None:
            self.image = _image
        if not isinstance(_image, Image):
            raise SpykeException(
                f'UUID: {image_id} points to a resource of type: {type(_image)}. Expected type: {Image.__name__}.')

        self.image = _image
