import dataclasses

from spyke import math
from spyke.assets.asset import Asset
from spyke.graphics import gl


@dataclasses.dataclass(slots=True)
class Glyph:
    size: math.Vector2
    bearing: math.Vector2
    advance: int
    texture_pos: math.Vector2
    texture_size: math.Vector2

@dataclasses.dataclass(eq=False)
class Font(Asset):
    _texture: gl.Texture = dataclasses.field(init=False)
    _glyphs: dict[str, Glyph] = dataclasses.field(init=False)
    _base_size: int = dataclasses.field(init=False)
    _name: str = dataclasses.field(init=False)

    def unload(self):
        self._texture.delete()

    def get_glyph(self, char: str) -> Glyph:
        if char not in self._glyphs:
            return self._glyphs['\n']

        return self._glyphs[char]
