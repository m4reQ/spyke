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
from ..graphics import Renderer

from OpenGL.GL import glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
#endregion

def InitializeDefaultProcessors(scene: Scene):
	scene.AddProcessor(WindowEventProcessor(), priority = 1)
	scene.AddProcessor(TransformProcessor())
	scene.AddProcessor(ParticleProcessor())
	scene.AddProcessor(ScriptProcessor())
	if ImGui.IsInitialized():
		scene.AddProcessor(ImguiProcessor())
	scene.AddProcessor(RenderingProcessor(), priority = 99)

class RenderingProcessor(Processor):
	def Process(self, *args, **kwargs):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		if not "renderTarget" in kwargs.keys():
			Log("No render target bound. Nothing will be drawn.", LogLevel.Warning)
			return
		
		Renderer.BeginScene(kwargs["renderTarget"])
		for _, (sprite, transform, color) in self.world.GetComponents(SpriteComponent, TransformComponent, ColorComponent):
			Renderer.RenderQuad(transform.Matrix, tuple(color), sprite.TextureHandle, sprite.TilingFactor)
		
		for _, (line, color) in self.world.GetComponents(LineComponent, ColorComponent):
			Renderer.RenderLine(line.StartPos, line.EndPos, tuple(color))
		
		for _, particleComponent in self.world.GetComponent(ParticleSystemComponent):
			for particle in particleComponent.particlePool:
				if not particle.isAlive:
					continue

				Renderer.RenderParticle(particle.position, particle.size, particle.rotation, particle.color.to_tuple(), particle.texHandle)
		
		for _, (text, transform, color) in self.world.GetComponents(TextComponent, TransformComponent, ColorComponent):
			Renderer.RenderText(transform.Position, tuple(color), text.Font, text.Size, text.Text)
		Renderer.EndScene()

class TransformProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, transform in self.world.GetComponent(TransformComponent):
			if transform.ShouldRecalculate:
				transform.Recalculate()

		# if renderTarget.Camera.shouldRecalculate:
		# 	renderTarget.Camera.RecalculateMatrices()

class ScriptProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, script in self.world.GetComponent(ScriptComponent):
			script.Process()

class WindowEventProcessor(Processor):
	def Process(self, *args, **kwargs):
		event = EventHandler.PickEventByType(EventType.WindowResize)
		if event:
			GLCommand.Scissor(0, 0, event.Width, event.Height)
			GLCommand.Viewport(0, 0, event.Width, event.Height)
			
			Renderer.Resize(event.Width, event.Height)

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

		for _, particleComponent in self.world.GetComponent(ParticleSystemComponent):
			for particle in particleComponent.particlePool:
				if not particle.isAlive:
					continue

				particle.position += particle.velocity * dt
				particle.rotation += particle.rotationVelocity * dt
				particle.life -= dt

				if particleComponent.colorChange:
					particle.color = LerpVec4(particle.life / particleComponent.duration, particleComponent.colorEnd, particleComponent.colorBegin)
				
				if particleComponent.fadeOut:
					particle.color.w = LerpFloat(particle.life / particleComponent.duration, 0.0, 1.0)
				
				if particleComponent.sizeChange:
					particle.size = LerpVec2(particle.life / particleComponent.duration, particleComponent.sizeEnd, particleComponent.sizeBegin)

				if particle.life < 0.0:
					particle.isAlive = False