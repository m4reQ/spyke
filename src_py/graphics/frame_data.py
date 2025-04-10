import dataclasses
import typing as t
from collections import defaultdict

from spyke import math
from spyke.graphics import gl

if t.TYPE_CHECKING:
    from spyke.assets import Model
    from spyke.graphics.light_data import LightData
    from spyke.graphics.render_batch import RenderBatch

@dataclasses.dataclass(slots=True)
class FrameData:
    white_texture: 'gl.Texture'
    frame_width: int
    frame_height: int
    clear_color: 'math.Vector4' = dataclasses.field(default_factory=lambda: math.Vector4(0.0, 0.0, 0.0, 1.0))
    camera_view: 'math.Matrix4' = dataclasses.field(default_factory=math.Matrix4.identity)
    camera_projection: 'math.Matrix4' = dataclasses.field(default_factory=math.Matrix4.identity)
    camera_pos: 'math.Vector3' = dataclasses.field(default_factory=math.Vector3.zero)
    polygon_mode: 'gl.PolygonMode' = gl.PolygonMode.FILL
    batches: defaultdict['Model', list['RenderBatch']] = dataclasses.field(default_factory=lambda: defaultdict(list))
    lights: list['LightData'] = dataclasses.field(default_factory=list)

    def reset(self) -> None:
        self.batches.clear()
        self.lights.clear()
