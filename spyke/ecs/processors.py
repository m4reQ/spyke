#region Import
from .esper import Processor, World as Scene
from .components import *
from ..graphics import OrthographicCamera, Renderer
from ..enums import AudioState
from ..debugging import Log, LogLevel
from ..imgui import ImGui as _ImGui
from ..input import *
from ..utils import LerpVec2, LerpVec4, LerpFloat

#endregion

def InitializeDefaultProcessors(scene: Scene):
	scene.AddProcessor(WindowEventProcessor(), priority = 1)
	scene.AddProcessor(TransformProcessor())
	scene.AddProcessor(ParticleProcessor())
	scene.AddProcessor(ScriptProcessor())
	# if _ImGui.IsInitialized():
	# 	scene.AddProcessor(ImguiProcessor())

class TransformProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, transform in self.scene.GetComponent(TransformComponent):
			if transform.ShouldRecalculate:
				transform.Recalculate()

		# if renderTarget.Camera.shouldRecalculate:
		# 	renderTarget.Camera.RecalculateMatrices()

class ScriptProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, script in self.scene.GetComponent(ScriptComponent):
			script.Process()

class WindowEventProcessor(Processor):
	def Process(self, *args, **kwargs):
		event = EventHandler.PickEventByType(EventType.WindowResize)
		if event:
			Renderer.Resize(event.Width, event.Height)

class ImguiProcessor(Processor):
	def Process(self, *args, **kwargs):
		_ImGui.OnFrame()

class AudioProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, audio in self.scene.GetComponent(AudioComponent):
			state = audio.Handle.GetState()

class ParticleProcessor(Processor):
	def Process(self, *args, **kwargs):
		dt = self.scene.GetFrameTime()

		for _, particleComponent in self.scene.GetComponent(ParticleSystemComponent):
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