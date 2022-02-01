from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Optional, Sequence
    from spyke.enums import SwizzleTarget, SizedInternalFormat, SwizzleMask

import numpy as np
from spyke.enums import MinFilter, MagFilter, TextureFormat, WrapMode


class TextureSpec:
    __slots__ = (
        '__weakref__',
        'mipmaps',
        'min_filter',
        'mag_filter',
        'wrap_mode',
        'format',
        'texture_swizzle',
        'internal_format',
        '_swizzle_mask'
    )

    def __init__(self):
        self.mipmaps: int = 3
        self.min_filter: MinFilter = MinFilter.LinearMipmapLinear
        self.mag_filter: MagFilter = MagFilter.Linear
        self.wrap_mode: WrapMode = WrapMode.Repeat
        self.format: TextureFormat = TextureFormat.Rgba
        self.internal_format: Optional[SizedInternalFormat] = None
        self.texture_swizzle: Optional[SwizzleTarget] = None
        self._swizzle_mask: Optional[np.ndarray] = None

    @property
    def swizzle_mask(self) -> np.ndarray:
        return self._swizzle_mask

    @swizzle_mask.setter
    def swizzle_mask(self, value: Sequence[SwizzleMask]) -> None:
        self._swizzle_mask = np.array(value, dtype=np.int32)
