import numpy as np
from pygl.math import Matrix4, Vector4
from pygl.rendering import DrawMode
from pygl.textures import Texture

from spyke import debug

InstanceDtype = np.dtype([
    ('color', np.float32, (4,)),
    ('texture_idx', np.float32),
    ('transform', np.float32, (16,))])

class RenderBatch:
    def __init__(self,
                 max_instance_count: int,
                 max_texture_count: int,
                 draw_mode: DrawMode = DrawMode.TRIANGLES) -> None:
        self.max_instance_count = max_instance_count
        self.max_texture_count = max_texture_count
        self.current_instance = 0
        self.textures = list[Texture]()
        self.draw_mode = draw_mode
        self.instance_data = np.empty((max_instance_count,), dtype=InstanceDtype)

    # TODO Materials to store color and texture inside them
    @debug.profiled
    def try_add_instance(self,
                         transform: Matrix4,
                         color: Vector4,
                         texture: Texture | None) -> bool:
        if self._too_many_instances() or self._cannot_use_texture(texture):
            return False

        current_instance = self.instance_data[self.current_instance]
        current_instance[0] = np.frombuffer(color, dtype=np.float32)
        current_instance[1] = self._get_texture_index(texture)
        current_instance[2] = np.frombuffer(transform, dtype=np.float32)
        self.current_instance += 1

        return True

    def _too_many_instances(self) -> bool:
        return self.current_instance >= self.max_instance_count

    def _cannot_use_texture(self, texture: Texture | None) -> bool:
        if texture is None:
            return False

        return texture not in self.textures and len(self.textures) >= self.max_texture_count

    def _get_texture_index(self, texture: Texture | None) -> int:
        if texture is None:
            return 0

        try:
            return self.textures.index(texture)
        except ValueError:
            self.textures.append(texture)
            return len(self.textures)
