from ..rectangle import Rectangle


class Glyph:
    def __init__(self, width: int, height: int, bearing_x: int, bearing_y: int, advance: int, tex_rect: Rectangle, char: str):
        self.tex_rect = tex_rect
        self.width = width
        self.height = height
        self.bearing_x = bearing_x
        self.bearing_y = bearing_y
        self.advance = advance

        self._char = char

    def __repr__(self):
        return self._char
