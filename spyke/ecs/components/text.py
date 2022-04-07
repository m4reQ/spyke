from __future__ import annotations
from typing import Optional
from uuid import UUID
from dataclasses import dataclass
import glm

@dataclass
class TextComponent:
    text: str
    size: int
    color: glm.vec4
    font_id: Optional[UUID]