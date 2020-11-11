from .renderStats import RenderStats
from ...utils import Abstract

import glm

class RendererComponent(Abstract):
    def BeginScene(self, viewProjection: glm.mat4) -> None:
        pass

    def EndScene(self) -> None:
        pass

    def GetStats(self) -> RenderStats:
        pass