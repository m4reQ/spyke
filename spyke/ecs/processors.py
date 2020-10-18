from .esper import Processor
from .components import *
from ..graphics import Renderer, GLCommand, OrthographicCamera, RenderTarget
from ..enums import ClearMask, AudioState
from ..debug import Log, LogLevel

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

class AudioProcessor(Processor):
	def process(self, *args, **kwargs):
		for _, audio in self.world.get_component(AudioComponent):
			state = audio.Handle.GetState()
			