from ..rectangle import RectangleF


class Glyph:
    def __init__(self, width: int, height: int, bearingX: int, bearingY: int, advance: int, texRect: RectangleF, char: str):
        self.texRect = texRect
        self.width = width
        self.height = height
        self.bearingX = bearingX
        self.bearingY = bearingY
        self.advance = advance

        self._char = char

    def __repr__(self):
        return self._char
