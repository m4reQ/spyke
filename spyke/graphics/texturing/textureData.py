from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class TextureData:
    width: int = 0
    height: int = 0
    data: np.ndarray = np.empty((0, 0), dtype=np.float32)
