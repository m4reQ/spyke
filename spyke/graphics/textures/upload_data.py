import dataclasses

import numpy as np
from spyke.enums import PixelType, TextureFormat


@dataclasses.dataclass
class TextureUploadData:
    width: int
    height: int
    data: np.ndarray
    format: TextureFormat
    level: int = 0
    pixel_type: PixelType = PixelType.UnsignedByte
    image_size: int = 0
