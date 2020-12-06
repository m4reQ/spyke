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
from spyke.sceneLoader import SaveScene, LoadScene

class UserProcessor(Processor):
	def __init__(self):
		self.timer = Delayer(2.0)
	
	def Process(self, *args, **kwargs):
		if not self.timer.IsWaiting():
			part = self.world.ComponentForEntity(kwargs["ent"], ParticleSystemComponent)
			part.EmitParticles(5)

class Window(GlfwWindow):
	def __init__(self, windowSpec):
		super().__init__(windowSpec)

		debug.GLInfo.PrintInfo()

		InputHandler.Initialize(self)

		GLCommand.Scissor(0, 0, self.width, self.height)
		GLCommand.Viewport(0, 0, self.width, self.height)
		GLCommand.SetClearcolor(0.4, 0.2, 0.3)

		GLCommand.Enable(EnableCap.Blend)
		GLCommand.BlendFunction(BlendFactor.SrcAlpha, BlendFactor.OneMinusSrcAlpha)

		LoadScene("tests/newScene.scn")

		self.ent4 = EntityManager.CreateEntity("Particles")
		self.particleSystem1 = ParticleSystemComponent(Vector2(0.5, 0.5), 3.0, 50)
		self.particleSystem1.colorBegin = Color(1.0, 0.0, 1.0, 1.0)
		self.particleSystem1.colorEnd = Color(0.0, 1.0, 1.0, 1.0)
		self.particleSystem1.sizeBegin = Vector2(0.25, 0.25)
		self.particleSystem1.sizeEnd = Vector2(0.1, 0.1)
		self.particleSystem1.velocity = Vector2(0.1, 0.3)
		self.particleSystem1.rotationVelocity = 0.0
		self.particleSystem1.randomizeMovement = True
		self.particleSystem1.fadeOut = True
		self.particleSystem1.texHandle = "tests/test1.jpg"
		SceneManager.Current.AddComponent(self.ent4, self.particleSystem1)

		ImGui.Initialize(self)
		ImGui.UpdateScene()

		Renderer.Initialize(self.specs.Multisample)

		InitializeDefaultProcessors(SceneManager.Current)
		SceneManager.Current.AddProcessor(UserProcessor())

		#fbSpec = FramebufferSpecs(self.width, self.height)
		#fbSpec.Samples = 4
		#fbSpec.HasDepthAttachment = False
		self.camera = OrthographicCamera(0.0, 1.0, 0.0, 1.0)
		renderTarget = RenderTarget(self.camera)#, Framebuffer(fbSpec))
		self.renderTargetId = Renderer.AddRenderTarget(renderTarget)
		Renderer.BindRenderTarget(self.renderTargetId)

		RequestGC()

	def OnFrame(self):
		SceneManager.Current.Process(window = self, ent = self.ent4)
		#self.renderer.RenderFramebuffer(self.scene.ComponentForEntity(self.ent2, TransformComponent).Matrix, self.renderTarget.Framebuffer, self.renderTarget.Camera.viewProjectionMatrix)
		self.SetTitle(self.baseTitle + " | Frametime: " + str(round(SceneManager.Current.GetFrameTime(), 5)) + "s")

	def OnClose(self):
		ObjectManager.DeleteAll()
		ImGui.Close()

if __name__ == "__main__":
	specs = WindowSpecs(512, 512, "TestWindow", 4, 6)
	specs.Multisample = True
	specs.Samples = 4
	specs.Vsync = False
	
	win = Window(specs)
	win.Run()

	#input()