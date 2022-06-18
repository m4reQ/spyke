import typing as t
from dataclasses import dataclass
from uuid import UUID

import glm
import numpy as np

@dataclass
class RenderCommand:
    texture_id: int
    model_id: UUID
    transform: glm.mat4
    color: glm.vec4
    tiling_factor: glm.vec2
    entity_id: int
    texture_coords_override: t.Optional[np.ndarray] = None