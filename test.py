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

from spyke.inputHandler import InputHandler
from spyke.keys import *

class KeysProcessor(Processor):
	def Process(self, *args, **kwargs):
		ent = kwargs["ent"]
		if InputHandler.IsKeyDown(Keys.KeyA):
			system = self.world.ComponentForEntity(ent, ParticleComponent)

			for _ in range(5):
				system.EmitParticle()
				
		InputHandler.ClearKeys()

class Window(GlfwWindow):
	def __init__(self, windowSpec):
		super().__init__(windowSpec)

		debug.GLInfo.PrintInfo()

		InputHandler.Initialize(self.Api)

		GLCommand.Scissor(0, 0, self.width, self.height)
		GLCommand.Viewport(0, 0, self.width, self.height)
		GLCommand.SetClearcolor(1.0, 1.0, 1.0)

		GLCommand.Enable(EnableCap.Blend)
		GLCommand.BlendFunction(BlendFactor.SrcAlpha, BlendFactor.OneMinusSrcAlpha)

		self.scene = EntityManager.CreateScene("Test", True)
		self.scene.AddProcessor(KeysProcessor())

		self.renderer = Renderer()
		self.renderer.AddComponent(BasicRenderer())
		self.renderer.AddComponent(LineRenderer())
		#self.renderer.AddComponent(TextRenderer())
		self.renderer.AddComponent(ParticleRenderer())

		TextureManager.CreateBlankArray()
		self.texarray = TextureManager.CreateTextureArray(1920, 1080, 3)
		self.tex = TextureManager.LoadTexture("textures/test3.png", self.texarray)

		self.camera = OrthographicCamera(0.0, 1.0, 0.0, 1.0)

		#self.font = Font("tests/ArialNative.fnt", "tests/ArialNative.png")

		self.ent1 = EntityManager.CreateEntity(self.scene, "TestText")
		self.scene.AddComponent(self.ent1, ColorComponent(0.0, 1.0, 1.0, 0.7))
		self.scene.AddComponent(self.ent1, SpriteComponent(self.tex, (1.0, 1.0)))
		self.scene.AddComponent(self.ent1, TransformComponent(Vector3(0.5, 0.5, 0.0), Vector2(0.5, 0.5), 0.0))

		self.ent2 = EntityManager.CreateEntity(self.scene, "FOO")
		self.scene.AddComponent(self.ent2, TransformComponent(Vector3(0.01, 0.01, 0.0), Vector2(0.3, 0.3), 0.0))
		#self.scene.AddComponent(self.ent2, TextComponent("TEST", 30, self.font))
		self.scene.AddComponent(self.ent2, ColorComponent(1.0, 1.0, 1.0, 1.0))

		self.ent3 = EntityManager.CreateEntity(self.scene, "Line")
		self.scene.AddComponent(self.ent3, LineComponent(Vector3(0.2, 0.2, 0.02), Vector3(0.5, 0.5, 0.02)))
		self.scene.AddComponent(self.ent3, ColorComponent(0.3, 0.7, 0.5, 0.7))

		self.ent4 = EntityManager.CreateEntity(self.scene, "Particles")
		self.particleSystem1 = ParticleComponent(Vector2(0.3, 0.3), 3.0, NoTexture, 10)
		self.scene.AddComponent(self.ent4, self.particleSystem1)
		self.particleSystem1.SizeBegin = Vector2(0.007, 0.007)
		self.particleSystem1.SizeEnd = Vector2(0.05, 0.05)
		self.particleSystem1.ColorEnd = Color(1.0, 0.7, 0.1, 1.0)
		self.particleSystem1.Velocity = Vector2(0.0, 0.03)
		self.particleSystem1.VelocityVariation = Vector2(0.01, 0.01)
		self.particleSystem1.RotationDelta = 13.0
		self.particleSystem1.RandomizeMovement = True
		self.particleSystem1.Looping = True
		self.particleSystem1.Start()

		ImGui.BindScene(self.scene)
		ImGui.BindRenderer(self.renderer)
		ImGui.Initialize(self)

		InitializeDefaultProcessors(self.scene, self.renderer)

		self.renderTarget = RenderTarget(self.camera)

		CollectGarbage()
	def OnFrame(self):
		self.scene.Process(renderTarget = self.renderTarget, window = self, ent = self.ent4)
		self.SetTitle(self.baseTitle + " | Frametime: " + str(round(self.scene.GetFrameTime(), 5)) + "s")

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