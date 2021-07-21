import spyke
spyke.Init()

from spyke.window import GlfwWindow, WindowSpecs
from spyke.ecs import *
from spyke import ResourceManager
from spyke.graphics import Color, Renderer
from spyke.math import *

class TestWindow(GlfwWindow):
    def __init__(self):
        super().__init__(WindowSpecs(512, 512, "Imgui test"), True)

        ResourceManager.SetSceneCurrent(ResourceManager.CreateScene("empty"))
        # ResourceManager.GetCurrentScene().CreateEntity(
        #     components.TagComponent("quad"),
        #     components.SpriteComponent("", Vector2(1.0), Color(1.0, 1.0, 1.0, 1.0)),
        #     components.TransformComponent(Vector3(0.5, 0.5, 0.0), Vector3(1.0, 1.0, 0.0), Vector3(0.0)))

    def OnFrame(self):
        Renderer.RenderScene(ResourceManager.GetCurrentScene(), Matrix4(1.0))
        self.SetTitle(f"{self.baseTitle} | DrawTime: {Renderer.renderStats.drawTime:.5f}")

if __name__ == "__main__":
    win = TestWindow()
    win.Run()
