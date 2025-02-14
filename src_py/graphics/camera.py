import abc

from pygl.math import Matrix4

from spyke.math import Viewport3D


class Camera(abc.ABC):
    def __init__(self, viewport: Viewport3D) -> None:
        self.viewport = viewport

    @property
    def view(self) -> Matrix4:
        return Matrix4.identity()

    @property
    @abc.abstractmethod
    def projection(self) -> Matrix4: ...

class OrthographicCamera(Camera):
    def __init__(self, viewport: Viewport3D) -> None:
        super().__init__(viewport)

    @property
    def projection(self) -> Matrix4:
        return Matrix4.ortho(
            self.viewport.left,
            self.viewport.right,
            self.viewport.bottom,
            self.viewport.top,
            self.viewport.near,
            self.viewport.far)

class PerspectiveCamera(Camera):
    def __init__(self, viewport: Viewport3D, fov: float, aspect_ratio: float) -> None:
        super().__init__(viewport)

        self.fov = fov
        self.aspect_ratio = aspect_ratio

    @property
    def projection(self) -> Matrix4:
        return Matrix4.perspective(
            self.fov,
            self.aspect_ratio,
            self.viewport.near,
            self.viewport.far)
