import spyke
spyke.Init()

from spyke.window import GlfwWindow, WindowSpecs
from spyke.ecs import *
from spyke import ResourceManager
from spyke.graphics import Renderer
from spyke.math import *

class TestWindow(GlfwWindow):
    def __init__(self):
        super().__init__(WindowSpecs(512, 512, "Imgui test"), True)

        ResourceManager.LoadScene("tests/empty.scn")

    def OnFrame(self):
        Renderer.RenderScene(ResourceManager.GetCurrentScene(), Matrix4(1.0))

if __name__ == "__main__":
    win = TestWindow()
    win.Run()
