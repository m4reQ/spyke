from __future__ import annotations
import numpy as np


class TextureData:
    __slots__ = (
        '__weakref__',
        'width',
        'height',
        'data'
    )

    def __init__(self):
        self.width: int = 0
        self.height: int = 0
        self.data: np.ndarray = np.empty((0, 0), dtype=np.float32)
