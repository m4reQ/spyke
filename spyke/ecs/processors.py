from .esper import Processor, World as Scene
from .components import *
from ..graphics import Renderer, GLCommand, OrthographicCamera, RenderTarget
from ..enums import ClearMask, AudioState
from ..debug import Log, LogLevel
from ..events import WindowEvent
from ..imgui import ImGui
from ..inputHandler import InputHandler

def InitializeDefaultProcessors(scene: Scene, renderer: Renderer):
	scene.add_processor(RenderingProcessor(renderer))
	scene.add_processor(WindowEventProcessor())
	scene.add_processor(TransformProcessor())
	if ImGui.IsInitialized():
		scene.add_processor(ImguiProcessor())

class RenderingProcessor(Processor):
	def __init__(self, renderer: Renderer):
		self.__renderer = renderer

	def process(self, *args, **kwargs):
		try:
			renderTarget = kwargs["renderTarget"]
		except KeyError:
			Log("Renderer target not set.", LogLevel.Warning)
			return

		GLCommand.Clear(ClearMask.ColorBufferBit | ClearMask.DepthBufferBit)
		
		self.__renderer.BeginScene(renderTarget)

		for _, (sprite, transform, color) in self.world.get_components(SpriteComponent, TransformComponent, ColorComponent):
			self.__renderer.RenderQuad(transform.Matrix, tuple(color), sprite.TextureHandle, sprite.TilingFactor)
		
		for _, (text, transform, color) in self.world.get_components(TextComponent, TransformComponent, ColorComponent):
			self.__renderer.RenderText(transform.Position, tuple(color), text.Font, text.Size, text.Text)
		
		self.__renderer.EndScene()

class TransformProcessor(Processor):
	def process(self, *args, **kwargs):
		for _, transform in self.world.get_component(TransformComponent):
			if transform.ShouldRecalculate:
				transform.Recalculate()

class WindowEventProcessor(Processor):
	def process(self, *args, **kwargs):
		try:
			window = kwargs["window"]
		except KeyError:
			raise RuntimeError("Window handle not set in process method.")

		try:
			renderTarget = kwargs["renderTarget"]
		except KeyError:
			renderTarget = None

		if InputHandler.Resized():
			GLCommand.Scissor(0, 0, window.width, window.height)
			GLCommand.Viewport(0, 0, window.width, window.height)
			if renderTarget:
				renderTarget.Camera.ReinitProjectionMatrix(0.0, 1.0, 0.0, float(window.width) / window.height, renderTarget.Camera.zNear, renderTarget.Camera.zFar)

class ImguiProcessor(Processor):
	def process(self, *args, **kwargs):
		ImGui.OnFrame()

class AudioProcessor(Processor):
	def process(self, *args, **kwargs):
		for _, audio in self.world.get_component(AudioComponent):
			state = audio.Handle.GetState()


			