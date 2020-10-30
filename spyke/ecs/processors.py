#region Import
from .esper import Processor, World as Scene
from .components import *
from ..graphics import Renderer, GLCommand, OrthographicCamera, RenderTarget
from ..enums import ClearMask, AudioState
from ..debug import Log, LogLevel
from ..imgui import ImGui
from ..input import *
from ..utils import LerpVec2, LerpVec4

import numpy
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
		
		for _, (particleComponent) in self.world.GetComponent(ParticleComponent):
			for particle in particleComponent.ParticlePool:
				if not particle.IsActive:
					continue

				self.renderer.RenderParticle(particle.Transform, particle.Color.to_tuple(), particle.TexHandle)
		
		self.renderer.EndScene()

class TransformProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, transform in self.world.GetComponent(TransformComponent):
			if transform.ShouldRecalculate:
				transform.Recalculate()

class WindowEventProcessor(Processor):
	def Process(self, *args, **kwargs):
		event = EventHandler.PickEventByType(EventType.WindowResize)
		if event and not event.Handled:
			try:
				window = kwargs["window"]
			except KeyError:
				Log("Window handle not set as processing argument.", LogLevel.Warning)
				return
			
			GLCommand.Scissor(0, 0, window.width, window.height)
			GLCommand.Viewport(0, 0, window.width, window.height)

			renderer = self.world.GetProcessor(RenderingProcessor)
			if renderer:
				renderer.Resize(window.width, window.height)

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

		for _, (particleComponent) in self.world.GetComponent(ParticleComponent):
			if not particleComponent.Started or particleComponent.Ended:
				for particle in particleComponent.ParticlePool:
					particle.IsActive = False
				continue

			if particleComponent.TimeElapsed >= particleComponent.Duration:
				if not particleComponent.Looping:
					particleComponent.Ended = True
				else:
					particleComponent.TimeElapsed -= particleComponent.Duration

			for particle in particleComponent.ParticlePool:
				if not particle.IsActive:
					continue

				if particle.LifeRemaining <= 0.0:
					particle.IsActive = False
					continue
				
				particle.LifeRemaining -= dt
				particle.Position += particle.Velocity * dt
				particle.Rotation += particleComponent.RotationSpeed * dt

				life = particle.LifeRemaining / particle.LifeTime

				particle.Color = LerpVec4(life, particle.ColorBegin, particle.ColorEnd)
				if particleComponent.FadeAway:
					particle.Color.w = particle.Color.w * life

				size = LerpVec2(life, particle.SizeBegin, particle.SizeEnd)

				particle.Transform = CreateTransform(glm.vec3(particle.Position.x, particle.Position.y, 0.0), size, particle.Rotation)

			particleComponent.TimeElapsed += dt