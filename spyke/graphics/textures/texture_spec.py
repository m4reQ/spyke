import dataclasses

from spyke.enums import (MagFilter, MinFilter, SizedInternalFormat,
                         SwizzleMask, SwizzleTarget, WrapMode)


@dataclasses.dataclass
class TextureSpec:
    width: int
    height: int
    internal_format: SizedInternalFormat
    samples: int = 1
    mipmaps: int = 4
    min_filter: MinFilter = MinFilter.LinearMipmapLinear
    mag_filter: MagFilter = MagFilter.Linear
    wrap_mode: WrapMode = WrapMode.Repeat
    texture_swizzle: SwizzleTarget | None = None
    swizzle_mask: list[SwizzleMask] | None = None

    @property
    def is_multisampled(self) -> bool:
        return self.samples > 1

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)
