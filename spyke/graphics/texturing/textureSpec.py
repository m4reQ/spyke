from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from typing import Optional, Sequence
    from spyke.enums import SwizzleTarget, SizedInternalFormat, SwizzleMask

import numpy as np
from spyke.enums import MinFilter, MagFilter, TextureFormat, WrapMode
from dataclasses import dataclass


@dataclass
class TextureSpec:
    mipmaps: int = 3
    min_filter: MinFilter = MinFilter.LinearMipmapLinear
    mag_filter: MagFilter = MagFilter.Linear
    wrap_mode: WrapMode = WrapMode.Repeat
    format: TextureFormat = TextureFormat.Rgba
    texture_swizzle: Optional[SizedInternalFormat] = None
    internal_format: Optional[SwizzleTarget] = None
    pixel_alignment: int = 4
    _swizzle_mask: Optional[np.ndarray] = None

    @property
    def swizzle_mask(self) -> np.ndarray:
        return self._swizzle_mask

    @swizzle_mask.setter
    def swizzle_mask(self, value: Sequence[SwizzleMask]) -> None:
        self._swizzle_mask = np.array(value, dtype=np.int32)
