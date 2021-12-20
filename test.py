import spyke

# from spyke.ecs.components.sprite import SpriteComponent
from spyke.ecs.components.transform import TransformComponent
from spyke.ecs.components.tag import TagComponent
from spyke.ecs import components
from spyke import debug

from spyke.window import GlfwWindow, WindowSpecs
from spyke.graphics import *
from spyke.enums import *
from spyke import ResourceManager
from spyke.utils import *
from spyke.math import *

class Window(GlfwWindow):
	def __init__(self, windowSpec):
		super().__init__(windowSpec, True)
	
	def OnLoad(self):
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
		# ecs.CurrentScene.AddComponent(self.ent4, self.particleSystem1)

		self.camera = OrthographicCamera(0.0, 1.0, 0.0, 1.0)

		# ResourceManager.LoadScene("tests/scene.scn")

		# EventHandler.KeyDown += EventHook(self.MoveCamera)
	
	def MoveCamera(self, key: int, mods: int, repeated: bool):
		if key == Keys.KeyW:
			self.camera.Move(Vector3(0.0, 0.1, 0.0), self.frameTime)
		elif key == Keys.KeyS:
			self.camera.Move(Vector3(0.0, -0.1, 0.0), self.frameTime)
		elif key == Keys.KeyA:
			self.camera.Move(Vector3(-0.1, 0.0, 0.0), self.frameTime)
		elif key == Keys.KeyD:
			self.camera.Move(Vector3(0.1, 0.0, 0.0), self.frameTime)
		
		return False
		
	def OnFrame(self):
		if self.camera.shouldRecalculate:
			self.camera.RecalculateMatrices()
			
		# ResourceManager.GetCurrentScene().Process(dt = self.frameTime)
		# Renderer.RenderScene(ResourceManager.GetCurrentScene(), Matrix4(1.0))

		self.SetTitle(f"{self.baseTitle} | FrameTime: {self.frameTime:.5F} | FPS: {int(1 / self.frameTime)}")
		debug.get_gl_error()

if __name__ == "__main__":
	specs = WindowSpecs(1080, 720, "TestWindow")
	specs.samples = 2
	specs.vsync = True
	
	win = Window(specs)
	win.Run()