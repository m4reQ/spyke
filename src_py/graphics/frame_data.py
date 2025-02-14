import dataclasses
from collections import defaultdict

from pygl.commands import PolygonMode
from pygl.math import Matrix4, Vector4
from pygl.textures import Texture

from spyke.assets import Model
from spyke.graphics.render_batch import RenderBatch


@dataclasses.dataclass(slots=True)
class FrameData:
    white_texture: Texture
    frame_width: int
    frame_height: int
    clear_color: Vector4 = dataclasses.field(default_factory=lambda: Vector4(0.0, 0.0, 0.0, 1.0))
    camera_view: Matrix4 = dataclasses.field(default_factory=Matrix4.identity)
    camera_projection: Matrix4 = dataclasses.field(default_factory=Matrix4.identity)
    polygon_mode: PolygonMode = PolygonMode.FILL
    batches: defaultdict[Model, list[RenderBatch]] = dataclasses.field(default_factory=lambda: defaultdict(list))

    def reset(self) -> None:
        self.batches.clear()
