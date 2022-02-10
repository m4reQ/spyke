from __future__ import annotations
from spyke.enums import TextureFormat
from spyke.graphics.texturing import textureSpec
from dataclasses import dataclass
import numpy as np


@dataclass
class TextureData:
    specification: textureSpec
    texture_format: TextureFormat
    image_format: str
    pixels: np.ndarray


@dataclass
class CompressedTextureData(TextureData):
    block_size: int
