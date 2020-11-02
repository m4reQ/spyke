#region Import
from .esper import Processor, World as Scene
from .components import *
from ..graphics import Renderer, GLCommand, OrthographicCamera, RenderTarget
from ..enums import ClearMask, AudioState
from ..debug import Log, LogLevel
from ..imgui import ImGui
from ..input import *
from ..utils import LerpVec2, LerpVec4, LerpFloat
from ..transform import Vector3
#endregion

def InitializeDefaultProcessors(scene: Scene, renderer: Renderer):
	scene.AddProcessor(WindowEventProcessor(), priority = 1)
	scene.AddProcessor(TransformProcessor())
	scene.AddProcessor(ParticleProcessor())
	if ImGui.IsInitialized():
		scene.AddProcessor(ImguiProcessor())
	scene.AddProcessor(RenderingProcessor(renderer), priority = 99)

class RenderingProcessor(Processor):
	def __init__(self, renderer: Renderer):
		self.renderer = renderer

	def Process(self, *args, **kwargs):
		try:
			renderTarget = kwargs["renderTarget"]
		except KeyError:
			Log("Renderer target not set.", LogLevel.Warning)
			return

		GLCommand.Clear(ClearMask.ColorBufferBit | ClearMask.DepthBufferBit)
		
		self.renderer.BeginScene(renderTarget)

		for _, (sprite, transform, color) in self.world.GetComponents(SpriteComponent, TransformComponent, ColorComponent):
			self.renderer.RenderQuad(transform.Matrix, tuple(color), sprite.TextureHandle, sprite.TilingFactor)
		
		for _, (text, transform, color) in self.world.GetComponents(TextComponent, TransformComponent, ColorComponent):
			self.renderer.RenderText(transform.Position, tuple(color), text.Font, text.Size, text.Text)
		
		for _, (line, color) in self.world.GetComponents(LineComponent, ColorComponent):
			self.renderer.RenderLine(line.StartPos, line.EndPos, tuple(color))
		
		for _, particleComponent in self.world.GetComponent(ParticleComponent):
			for particle in particleComponent.particlePool:
				if not particle.isAlive:
					continue

				print(len([x for x in particleComponent.particlePool if x.isAlive]))

				self.renderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color.to_tuple(), particle.texHandle)
		
		self.renderer.EndScene()

class TransformProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, transform in self.world.GetComponent(TransformComponent):
			if transform.ShouldRecalculate:
				transform.Recalculate()

class WindowEventProcessor(Processor):
	def Process(self, *args, **kwargs):
		event = EventHandler.PickEventByType(EventType.WindowResize)
		if event:
			try:
				window = kwargs["window"]
			except KeyError:
				Log("Window handle not set as processing argument.", LogLevel.Warning)
				return
			
			GLCommand.Scissor(0, 0, event.Width, event.Height)
			GLCommand.Viewport(0, 0, event.Width, event.Height)
			
			try:
				renderer = kwargs["renderer"]
				if renderer:
					renderer.Resize(window.width, window.height)
			except KeyError:
				pass

class ImguiProcessor(Processor):
	def Process(self, *args, **kwargs):
		ImGui.OnFrame()

class AudioProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, audio in self.world.GetComponent(AudioComponent):
			state = audio.Handle.GetState()

class ParticleProcessor(Processor):
	def Process(self, *args, **kwargs):
		dt = self.world.GetFrameTime()

		for _, particleComponent in self.world.GetComponent(ParticleComponent):
			for particle in particleComponent.particlePool:
				if not particle.isAlive:
					continue

				particle.position += particle.velocity * dt
				particle.rotation += particle.rotationVelocity * dt
				particle.life -= dt

				if particleComponent.colorChange:
					particle.color = LerpVec4(particle.life, particleComponent.colorBegin, particleComponent.colorEnd)
				
				if particleComponent.fadeOut:
					particle.color.w = LerpFloat(particle.life, 1.0, 0.0)
				
				if particleComponent.sizeChange:
					particle.size = LerpVec2(particle.life, particleComponent.sizeBegin, particleComponent.sizeEnd)

				if particle.life < 0.0:
					particle.isAlive = False