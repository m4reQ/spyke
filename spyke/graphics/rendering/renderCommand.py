from dataclasses import dataclass
from uuid import UUID
import glm
import numpy as np

@dataclass
class RenderCommand:
    # TODO: Decide if we want to use image id or the texture itself
    image_id: UUID
    model_id: UUID
    transform: glm.mat4
    color: glm.vec4
    tiling_factor: glm.vec2
    entity_id: int
    custom_texture_coords: np.ndarray