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
from spyke.keys import *
from spyke.input import *

class KeyProcessor(Processor):
	def Process(self, *args, **kwargs):
		e = EventHandler.PickEventByType(EventType.KeyPressed)

		if e and e.KeyCode == Keys.KeyA.Glfw:
			ent = kwargs["ent"]
			part = self.world.ComponentForEntity(ent, ParticleComponent)
			part.EmitParticles(5)

class Window(GlfwWindow):
	def __init__(self, windowSpec):
		super().__init__(windowSpec)

		debug.GLInfo.PrintInfo()

		InputHandler.Initialize(self)

		GLCommand.Scissor(0, 0, self.width, self.height)
		GLCommand.Viewport(0, 0, self.width, self.height)
		GLCommand.SetClearcolor(0.7, 0.2, 0.5)

		GLCommand.Enable(EnableCap.Blend)
		GLCommand.BlendFunction(BlendFactor.SrcAlpha, BlendFactor.OneMinusSrcAlpha)

		self.scene = EntityManager.CreateScene("Test", True)

		self.renderer = Renderer()
		self.renderer.AddComponent(BasicRenderer())
		self.renderer.AddComponent(LineRenderer())
		self.renderer.AddComponent(TextRenderer())
		self.renderer.AddComponent(ParticleRenderer())
		self.renderer.AddComponent(PostRenderer())

		TextureManager.CreateBlankArray()
		self.texarray = TextureManager.CreateTextureArray(1920, 1080, 3)
		self.tex = TextureManager.LoadTexture("textures/test2.jpg", self.texarray)

		self.camera = OrthographicCamera(0.0, 1.0, 0.0, 1.0)

		self.font = Font("textures/test.fnt", "textures/test.png")

		self.ent1 = EntityManager.CreateEntity(self.scene, "TestText")
		self.scene.AddComponent(self.ent1, ColorComponent(0.0, 1.0, 1.0, 0.7))
		self.scene.AddComponent(self.ent1, SpriteComponent(self.tex, (1.0, 1.0)))
		self.scene.AddComponent(self.ent1, TransformComponent(Vector3(0.5, 0.5, 0.0), Vector2(0.5, 0.5), 0.0))

		self.ent2 = EntityManager.CreateEntity(self.scene, "FOO")
		self.scene.AddComponent(self.ent2, TransformComponent(Vector3(0.6, 0.01, 0.0), Vector2(0.3, 0.3), 0.0))
		self.scene.AddComponent(self.ent2, TextComponent("TEST", 30, self.font))
		self.scene.AddComponent(self.ent2, ColorComponent(1.0, 1.0, 1.0, 1.0))

		self.ent3 = EntityManager.CreateEntity(self.scene, "Line")
		self.scene.AddComponent(self.ent3, LineComponent(Vector3(0.2, 0.2, 0.02), Vector3(0.5, 0.5, 0.02)))
		self.scene.AddComponent(self.ent3, ColorComponent(0.3, 0.7, 0.5, 0.7))

		self.ent4 = EntityManager.CreateEntity(self.scene, "Particles")
		self.particleSystem1 = ParticleComponent(Vector2(0.5, 0.5), 3.0, 50)
		self.particleSystem1.colorBegin = Color(1.0, 0.0, 1.0, 1.0)
		self.particleSystem1.colorEnd = Color(0.0, 1.0, 1.0, 1.0)
		self.particleSystem1.sizeBegin = Vector2(0.1, 0.1)
		self.particleSystem1.sizeEnd = Vector2(0.1, 0.1)
		self.particleSystem1.velocity = Vector2(0.3, 0.2)
		self.particleSystem1.rotationVelocity = 0.5
		self.particleSystem1.randomizeMovement = True
		self.particleSystem1.fadeOut = True
		self.particleSystem1.texHandle = self.tex
		self.scene.AddComponent(self.ent4, self.particleSystem1)

		ImGui.BindScene(self.scene)
		ImGui.BindRenderer(self.renderer)
		ImGui.Initialize(self)

		InitializeDefaultProcessors(self.scene, self.renderer)
		self.scene.AddProcessor(KeyProcessor())

		fbSpec = FramebufferSpecs(self.width, self.height)
		fbSpec.Samples = 4
		fbSpec.HasDepthAttachment = False
		self.renderTarget = RenderTarget(self.camera, Framebuffer(fbSpec))

		CollectGarbage()

	def OnFrame(self):
		self.scene.Process(renderTarget = self.renderTarget, window = self, ent = self.ent4, renderer = self.renderer)
		self.renderer.RenderFramebuffer(self.scene.ComponentForEntity(self.ent2, TransformComponent).Matrix, self.renderTarget.Framebuffer, self.renderTarget.Camera.viewProjectionMatrix)
		self.SetTitle(self.baseTitle + " | Frametime: " + str(round(self.scene.GetFrameTime(), 5)) + "s")

	def OnClose(self):
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