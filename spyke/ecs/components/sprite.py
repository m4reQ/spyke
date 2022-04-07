from __future__ import annotations
from typing import Optional
from uuid import UUID
from dataclasses import dataclass
import glm

@dataclass
class SpriteComponent:
    color: glm.vec4
    image_id: Optional[UUID]
    tiling_factor: glm.vec2