from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    import numpy as np

from spyke.enums import TextureFormat


class TextureData:
    __slots__ = (
        '__weakref__',
        'width',
        'height',
        'data',
        'format'
    )

    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.data: np.ndarray = None
        self.format: TextureFormat = TextureFormat.Rgba
