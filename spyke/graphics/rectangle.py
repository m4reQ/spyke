class Rectangle:
    @classmethod
    def one(cls):
        return cls(0.0, 0.0, 1.0, 1.0)

    def __init__(self, x: float, y: float, width: float, height: float):
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return all(self.x == other.x, self.y == other.y, self.width == other.width, self.height == other.height)

    def to_screen_coordinates(self, screen_width: int, screen_height: int):
        x_mapped = int(self.x * screen_width)
        y_mapped = int(self.y * screen_height)
        width_mapped = int(self.width * screen_height)
        height_mapped = int(self.height * screen_height)

        return Rectangle(x_mapped, y_mapped, width_mapped, height_mapped)

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    @property
    def top(self):
        return self.y
