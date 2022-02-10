from __future__ import annotations
from spyke.graphics.glyph import Glyph
from spyke.loaders.textureData import TextureData
from typing import Dict
from dataclasses import dataclass


@dataclass
class FontData:
    texture_data: TextureData
    font_name: str
    glyphs: Dict[str, Glyph]
