if __debug__:
	import spyke
	spyke.DEBUG_ENABLE = True
	spyke.DEBUG_LOG_TIME = True
	spyke.DEBUG_COLOR = True

	from spyke import debug
	debug.Log("Debugging enabled.", debug.LogLevel.Info)

from spyke.imgui import ImGui

from spyke.graphics import *
from spyke.window import GlfwWindow, WindowSpecs

from spyke.ecs import EntityManager
from spyke.ecs.components import *
from spyke.ecs.processors import *

from spyke.graphics import *
from spyke.enums import *

from spyke.utils import CollectGarbage

from spyke.transform import *

from spyke.events import WindowEvent
from spyke.inputHandler import InputHandler

class Window(GlfwWindow):
	def __init__(self, windowSpec):
		super().__init__(windowSpec)

		debug.GLInfo.PrintInfo()

		InputHandler.Initialize(self.Api)

		GLCommand.Scissor(0, 0, self.width, self.height)
		GLCommand.Viewport(0, 0, self.width, self.height)

		GLCommand.Enable(EnableCap.Blend)
		GLCommand.BlendFunction(BlendFactor.SrcAlpha, BlendFactor.OneMinusSrcAlpha)

		self.scene = EntityManager.CreateScene("Test", True)
		self.renderer = Renderer(Shader.Basic2D())
		self.renderer.AddComponent(RendererTarget.TextRenderer, Shader.BasicText())
		self.renderer.AddComponent(RendererTarget.LineRenderer, Shader.BasicLine())

		TextureManager.CreateBlankArray()
		self.texarray = TextureManager.CreateTextureArray(1920, 1080, 3)
		self.tex = TextureManager.LoadTexture("tests/test1.jpg", self.texarray)

		self.camera = OrthographicCamera(0.0, 1.0, 0.0, 1.0)

		self.font = Font("tests/ArialNative.fnt", "tests/ArialNative.png")

		self.ent1 = EntityManager.CreateEntity(self.scene, "TestText")
		self.scene.add_component(self.ent1, ColorComponent(0.0, 1.0, 1.0, 0.7))
		self.scene.add_component(self.ent1, SpriteComponent(self.tex, (2.0, 2.0)))
		self.scene.add_component(self.ent1, TransformComponent(Vector3(0.5, 0.5, 0.0), Vector2(0.5, 0.5), 17.0))

		self.ent2 = EntityManager.CreateEntity(self.scene, "FOO")
		self.scene.add_component(self.ent2, TransformComponent(Vector3(0.01, 0.01, 0.0), Vector2(0.3, 0.3), 0.0))
		self.scene.add_component(self.ent2, TextComponent("TEST", 30, self.font))
		self.scene.add_component(self.ent2, ColorComponent(1.0, 1.0, 1.0, 1.0))

		self.ent3 = EntityManager.CreateEntity(self.scene, "Line")
		self.scene.add_component(self.ent3, LineComponent(Vector3(0.2, 0.2, 0.02), Vector3(0.5, 0.5, 0.02)))
		self.scene.add_component(self.ent3, ColorComponent(0.3, 0.7, 0.5, 0.7))

		self.ent4 = EntityManager.CreateEntity(self.scene, "Framebuffer")
		self.scene.add_component

		ImGui.BindScene(self.scene)
		ImGui.BindRenderer(self.renderer)
		ImGui.Initialize(self)

		InitializeDefaultProcessors(self.scene, self.renderer)

		self.renderTarget = RenderTarget(self.camera)

		CollectGarbage()
	
	def Render(self):
		self.scene.process(renderTarget = self.renderTarget, window = self)
	
	def Update(self):
		processingTime = sum(self.scene.process_times.values())
		self.SetTitle(self.baseTitle + " | Frametime: " + str(round(processingTime, 5)) + "s")
	
	def Close(self):
		ObjectManager.DeleteAll()
		ImGui.Close()
		CollectGarbage()

if __name__ == "__main__":
	specs = WindowSpecs(512, 512, "TestWindow", 4, 5)
	specs.Multisample = True
	specs.Samples = 4
	specs.Vsync = False
	
	win = Window(specs)
	win.Run()

	input()