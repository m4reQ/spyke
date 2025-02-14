class Viewport2D:
    def __init__(self,
                 left: float,
                 right: float,
                 bottom: float,
                 top: float) -> None:
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top

    def to_viewport_3d(self) -> Viewport3D: ...

class Viewport3D:
    def __init__(self,
                 left: float,
                 right: float,
                 bottom: float,
                 top: float,
                 near: float,
                 far: float) -> None:
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far

    def to_viewport_2d(self) -> Viewport2D: ...
