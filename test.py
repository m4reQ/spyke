import spyke
spyke.Init()

from spyke.debugging import Debug, LogLevel

from spyke.imgui import ImGui
from spyke.window import GlfwWindow, WindowSpecs
from spyke.graphics import *
from spyke.enums import *
from spyke.managers import *
from spyke.utils import *
from spyke.math import *
from spyke.input import *
from spyke import ecs

#RendererSettings.ClearColor = Vector4(0.8, 0.9, 0.3, 1.0)

class Window(GlfwWindow):
	def __init__(self, windowSpec, imgui):
		super().__init__(windowSpec, imgui)
	
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

		#ImGui.Initialize(self)
		#ImGui.UpdateScene()

		# TextureManager.LoadTexture("tests/test1.jpg")
		# TextureManager.LoadTexture("tests/test2.png")

		# FontManager.CreateFont("tests/ArialNative.fnt", "tests/ArialNative.png", "Arial")

		# SceneManager.CreateScene("TEST", True)
		# InitializeDefaultProcessors(ecs.CurrentScene)

		# ent1 = ecs.CurrentScene.CreateEntity() #VIOLET first
		# ecs.CurrentScene.AddComponent(ent1, TransformComponent(Vector3(0.0, 0.5, 0.3), Vector3(0.5, 0.5, 0.0), Vector3(0.0, 0.0, 90.0)))
		# ecs.CurrentScene.AddComponent(ent1, SpriteComponent("", Vector2(1.0, 1.0), Color(1.0, 0.0, 1.0, 0.8)))

		# ent2 = ecs.CurrentScene.CreateEntity() #YELLOW first
		# ecs.CurrentScene.AddComponent(ent2, TransformComponent(Vector3(0.0, 0.1, 0.2), Vector3(0.2, 0.3, 0.0), Vector3(0.0)))
		# ecs.CurrentScene.AddComponent(ent2, SpriteComponent("", Vector2(1.0, 1.0), Color(1.0, 1.0, 0.0, 0.7)))

		# ent3 = ecs.CurrentScene.CreateEntity() #TEXTURE last
		# ecs.CurrentScene.AddComponent(ent3, TransformComponent(Vector3(0.0, 0.0, 0.4), Vector3(0.7, 0.6, 0.0), Vector3(0.0)))
		# ecs.CurrentScene.AddComponent(ent3, SpriteComponent("tests/test2.png", Vector2(1.0, 1.0), Color(1.0, 1.0, 1.0, 1.0)))

		# ent4 = ecs.CurrentScene.CreateEntity()
		# ecs.CurrentScene.AddComponent(ent4, TransformComponent(Vector3(0.5, 0.5, 0.1), Vector3(1.0), Vector3(0.0)))
		# ecs.CurrentScene.AddComponent(ent4, TextComponent("TEST", 40, "Arial", Color(0.0, 1.0, 1.0, 0.7)))

		# ecs.CurrentScene.AddProcessor(UserProcessor())

		self.camera = OrthographicCamera(0.0, 1.0, 0.0, 1.0)

		FontManager.CreateFont("tests/ArialNative.fnt", "tests/ArialNative.png", "arial")
		ecs.CreateScene("Test Scene").MakeCurrent()

		ecs.Scene.Current.CreateEntity(
			ecs.components.TagComponent("tex"),
			ecs.components.TransformComponent(Vector3(-0.3, -0.3, 0.0), Vector3(0.5, 0.5, 0.0), Vector3(0.0)),
			ecs.components.SpriteComponent("Tests/test1.jpg", Vector2(2.0), Color(1.0, 1.0, 1.0, 1.0))
		)

		ecs.Scene.Current.CreateEntity(
			ecs.components.TagComponent("tex2"),
			ecs.components.TransformComponent(Vector3(0.6, 0.6, 0.0), Vector3(0.3, 0.6, 0.0), Vector3(300.0)),
			ecs.components.SpriteComponent("Tests/test2.png", Vector2(1.0), Color(1.0, 1.0, 0.8, 0.7))
		)

		ecs.Scene.Current.CreateEntity(
			ecs.components.TagComponent("violet"),
			ecs.components.TransformComponent(Vector3(0.0, 0.0, 0.0), Vector3(0.3, 0.3, 0.0), Vector3(0.0)),
			ecs.components.SpriteComponent("", Vector2(1.0), Color(1.0, 0.0, 0.7, 0.5))
		)

		ecs.Scene.Current.CreateEntity(
			ecs.components.TagComponent("yellow"),
			ecs.components.TransformComponent(Vector3(0.1, 0.1, 0.0), Vector3(0.2, 0.4, 0.0), Vector3(0.0)),
			ecs.components.SpriteComponent("", Vector2(1.0), Color(1.0, 1.0, 0.2, 0.3))
		)

		ecs.Scene.Current.CreateEntity(
			ecs.components.TagComponent("green"),
			ecs.components.TransformComponent(Vector3(-0.75, -0.75, 0.0), Vector3(0.3, 0.3, 0.0), Vector3(0.0)),
			ecs.components.SpriteComponent("", Vector2(1.0), Color(0.0, 1.0, 0.0, 1.0))
		)
		
		ecs.Scene.Current.CreateEntity(
			ecs.components.TagComponent("text"),
			ecs.components.TransformComponent(Vector3(0.5, 0.5, 0.0), Vector3(0.0), Vector3(0.0)),
			ecs.components.TextComponent("Hello world!", 40, "arial", Color(0.0, 1.0, 1.0, 1.0))
		)

		#SaveScene("test.scn")
		EventHandler.KeyDown += EventHook(self.MoveCamera)
	
	def MoveCamera(self, key: int, mods: int, repeated: bool):
		if key == Keys.KeyW:
			self.camera.Move(Vector3(0.0, 0.2, 0.0), self.frameTime)
		elif key == Keys.KeyS:
			self.camera.Move(Vector3(0.0, -0.2, 0.0), self.frameTime)
		elif key == Keys.KeyA:
			self.camera.Move(Vector3(-0.2, 0.0, 0.0), self.frameTime)
		elif key == Keys.KeyD:
			self.camera.Move(Vector3(0.2, 0.0, 0.0), self.frameTime)
		
		return False
		
	def OnFrame(self):
		if self.camera.shouldRecalculate:
			self.camera.RecalculateMatrices()

		ecs.Scene.Current.Process(dt = self.frameTime)
		Renderer.RenderScene(ecs.Scene.Current, Matrix4(1.0))

		self.SetTitle(f"{self.baseTitle} | FrameTime: {self.frameTime:.5F} | FPS: {int(1 / self.frameTime)}")

if __name__ == "__main__":
	specs = WindowSpecs(512, 512, "TestWindow")
	specs.samples = 1
	specs.vsync = True
	
	win = Window(specs, False)
	win.Run()