import dataclasses

from pygl.math import Vector2
from pygl.textures import Texture
from spyke.assets.asset import Asset


@dataclasses.dataclass(slots=True)
class Glyph:
    size: Vector2
    bearing: Vector2
    advance: int
    texture_pos: Vector2
    texture_size: Vector2

@dataclasses.dataclass(eq=False)
class Font(Asset):
    _texture: Texture = dataclasses.field(init=False)
    _glyphs: dict[str, Glyph] = dataclasses.field(init=False)
    _base_size: int = dataclasses.field(init=False)
    _name: str = dataclasses.field(init=False)

    def unload(self):
        self._texture.delete()

    def get_glyph(self, char: str) -> Glyph:
        if char not in self._glyphs:
            return self._glyphs['\n']

        return self._glyphs[char]
