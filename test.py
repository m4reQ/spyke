if __debug__:
	import spyke
	spyke.DEBUG_ENABLE = True
	spyke.DEBUG_LOG_TIME = True
	spyke.DEBUG_COLOR = True

	from spyke import debug
	debug.Log("Debugging enabled.", debug.LogLevel.Info)

from spyke.ecs.components import *
from spyke.ecs.processors import *

#from spyke.imgui import ImGui
from spyke.window import GlfwWindow, WindowSpecs
from spyke.graphics import *
from spyke.enums import *
from spyke.managers import *
from spyke.utils import *
from spyke.transform import *
from spyke.input import *
from spyke.sceneLoader import SaveScene

class UserProcessor(Processor):
	def __init__(self):
		self.delayer = Delayer(2.0)
		self.system = None
	
	def LateInit(self):
		self.system = self.scene.ComponentForEntity(EntityManager.GetEntity("Particles"), ParticleSystemComponent)

	def Process(self, *args, **kwargs):
		if not self.delayer.IsWaiting():
			self.system.EmitParticle()

class Window(GlfwWindow):
	def __init__(self, windowSpec):
		super().__init__(windowSpec)

		debug.GLInfo.PrintInfo()

		InputHandler.Initialize(self)
		# LoadScene("tests/newScene.scn")

		# self.ent4 = EntityManager.CreateEntity("Particles")
		# self.particleSystem1 = ParticleSystemComponent(Vector2(0.5, 0.5), 3.0, 50)
		# self.particleSystem1.colorBegin = Color(1.0, 0.0, 1.0, 1.0)
		# self.particleSystem1.colorEnd = Color(0.0, 1.0, 1.0, 1.0)
		# self.particleSystem1.sizeBegin = Vector2(0.25, 0.25)
		# self.particleSystem1.sizeEnd = Vector2(0.1, 0.1)
		# self.particleSystem1.velocity = Vector2(0.1, 0.3)
		# self.particleSystem1.rotationVelocity = 0.0
		# self.particleSystem1.randomizeMovement = True
		# self.particleSystem1.fadeOut = True
		# self.particleSystem1.texHandle = "tests/test1.jpg"
		# SceneManager.Current.AddComponent(self.ent4, self.particleSystem1)

		#ImGui.Initialize(self)
		#ImGui.UpdateScene()

		Renderer.Initialize(self.width, self.height)

		TextureManager.LoadTexture("tests/test1.jpg")
		TextureManager.LoadTexture("tests/test2.png")

		SceneManager.CreateScene("TEST", True)
		InitializeDefaultProcessors(SceneManager.Current)

		ent1 = SceneManager.Current.CreateEntity()
		SceneManager.Current.AddComponent(ent1, TransformComponent(Vector3(0.0, 0.5, 0.1), Vector3(0.5, 0.5, 0.0), Vector3(0.0, 0.0, 90.0)))
		SceneManager.Current.AddComponent(ent1, SpriteComponent("", Vector2(1.0, 1.0), Color(1.0, 0.0, 1.0, 1.0)))

		ent2 = SceneManager.Current.CreateEntity()
		SceneManager.Current.AddComponent(ent2, TransformComponent(Vector3(0.0, 0.1, 0.0), Vector3(0.2, 0.3, 0.0), Vector3(0.0, 0.0, 0.0)))
		SceneManager.Current.AddComponent(ent2, SpriteComponent("", Vector2(1.0, 1.0), Color(1.0, 1.0, 0.0, 1.0)))

		ent3 = SceneManager.Current.CreateEntity()
		SceneManager.Current.AddComponent(ent3, TransformComponent(Vector3(0.0, 0.0, 1.0), Vector3(1.0), Vector3(0.0)))
		SceneManager.Current.AddComponent(ent3, SpriteComponent("tests/test2.png", Vector2(1.0, 1.0), Color(1.0, 1.0, 1.0, 1.0)))
		# SceneManager.Current.AddProcessor(UserProcessor())

		fbSpec = FramebufferSpec(self.width, self.height)
		fbSpec.Samples = 4
		fbSpec.HasDepthAttachment = False ########################
		fbSpec.Color = Color(0.0, 1.0, 1.0, 1.0)

		#self.framebuffer = Framebuffer(fbSpec)

		self.camera = OrthographicCamera(0.0, 1.0, 0.0, 1.0)
		self.renderTarget = RenderTarget(self.camera)

		self.posTEST = glm.translate(glm.mat4(1.0), glm.vec3(-1.0, -1.0, 0.0))
		self.posTEST = glm.scale(self.posTEST, glm.vec3(2.0, 2.0, 0.0))

		#SaveScene("test.scn")

		RequestGC()

	def OnFrame(self):
		SceneManager.Current.Process(window = self)
		Renderer.RenderScene(SceneManager.Current, self.camera.viewProjectionMatrix)#, self.framebuffer)
		#Renderer.RenderFramebuffer(Vector3(0.0), Vector3(1.0, 1.0, 0.0), Vector3(0.0), self.framebuffer)
		#Renderer.PostRender(self.posTEST, self.renderTarget, Color(0.0, 1.0, 0.5, 1.0))
		self.SetTitle(self.baseTitle + " | FPS: {0:.2f} | Rendertime: {1:.5f}s".format(1.0 / RenderStats.DrawTime, RenderStats.DrawTime))
		#self.SetTitle(self.baseTitle + " | Frametime: " + str(round(SceneManager.Current.GetFrameTime(), 5)) + "s")

	def OnClose(self):
		ObjectManager.DeleteAll()
		#ImGui.Close()

if __name__ == "__main__":
	specs = WindowSpecs(512, 512, "TestWindow", 4, 5)
	specs.Multisample = True
	specs.Samples = 4
	specs.Vsync = False
	
	win = Window(specs)
	win.Run()