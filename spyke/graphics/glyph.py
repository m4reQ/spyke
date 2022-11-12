import dataclasses

import glm
import numpy as np


@dataclasses.dataclass
class Glyph:
    __slots__ = (
        '__weakref__',
        'tex_coords',
        'size',
        'bearing',
        'advance'
    )

    size: glm.ivec2
    bearing: glm.ivec2
    advance: int
    tex_coords: np.ndarray
