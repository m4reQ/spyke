import typing as t

import numpy as np

from spyke import debug, math
from spyke.graphics import gl

InstanceDtype = np.dtype([
    ('color', np.float32, (4,)),
    ('albedo_idx', np.float32),
    ('specular_idx', np.float32),
    ('transform', np.float32, (16,))])

class RenderBatch:
    def __init__(self,
                 max_instance_count: int,
                 max_texture_count: int,
                 draw_mode: gl.DrawMode = gl.DrawMode.TRIANGLES) -> None:
        self.max_instance_count = max_instance_count
        self.max_texture_count = max_texture_count
        self.current_instance = 0
        self.textures = list[gl.Texture]()
        self.draw_mode = draw_mode
        self.instance_data = np.empty((max_instance_count,), dtype=InstanceDtype)

    # TODO Materials to store color and texture inside them
    @debug.profiled
    def try_add_instance(self,
                         transform: math.Matrix4,
                         color: math.Vector4,
                         textures: t.Sequence[gl.Texture]) -> bool:
        if self._too_many_instances() or self._cannot_use_textures(textures):
            return False

        current_instance = self.instance_data[self.current_instance]
        current_instance[0] = np.frombuffer(color, dtype=np.float32)
        current_instance[1] = self._get_texture_index(textures[0]) # albedo
        current_instance[2] = self._get_texture_index(textures[1]) # specular
        current_instance[3] = np.frombuffer(transform, dtype=np.float32)
        self.current_instance += 1

        return True

    def _too_many_instances(self) -> bool:
        return self.current_instance >= self.max_instance_count

    def _cannot_use_textures(self, textures: t.Iterable[gl.Texture]) -> bool:
        for texture in textures:
            if texture is not None and texture not in self.textures and len(self.textures) >= self.max_texture_count:
                return True

        return False

    def _get_texture_index(self, texture: gl.Texture | None) -> int:
        if texture is None:
            return 0

        try:
            return self.textures.index(texture)
        except ValueError:
            self.textures.append(texture)
            return len(self.textures)
