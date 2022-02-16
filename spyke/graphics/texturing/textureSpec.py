from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Optional, Sequence
    from spyke.enums import SwizzleTarget, SwizzleMask

import numpy as np
from spyke.enums import MinFilter, MagFilter, WrapMode, _SizedInternalFormat, SizedInternalFormat
from dataclasses import dataclass


@dataclass
class TextureSpec:
    width: int = 0
    height: int = 0
    mipmaps: int = 3
    min_filter: MinFilter = MinFilter.LinearMipmapLinear
    mag_filter: MagFilter = MagFilter.Linear
    wrap_mode: WrapMode = WrapMode.Repeat
    texture_swizzle: Optional[SwizzleTarget] = None
    internal_format: _SizedInternalFormat = SizedInternalFormat.Rgba8
    _swizzle_mask: Optional[np.ndarray] = None

    @property
    def swizzle_mask(self) -> np.ndarray:
        return self._swizzle_mask or np.zeros((4,), dtype=np.int32)

    @swizzle_mask.setter
    def swizzle_mask(self, value: Sequence[SwizzleMask]) -> None:
        self._swizzle_mask = np.array(value, dtype=np.int32)
