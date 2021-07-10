#region Import
from .esper import Processor
from .components import *
from ..math import LerpVec2, LerpVec4, LerpFloat
#endregion

class TransformProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, transform in self.scene.GetComponent(TransformComponent):
			if transform.shouldRecalculate:
				transform.RecalculateMatrices()
		
		for _, cameraComponent in self.scene.GetComponent(CameraComponent):
			if cameraComponent.shouldRecalculate:
				cameraComponent.RecalculateMatrices()
				
class AudioProcessor(Processor):
	def Process(self, *args, **kwargs):
		for _, audio in self.scene.GetComponent(AudioComponent):
			state = audio.Handle.GetState()

class ParticleProcessor(Processor):
	def Process(self, dt: float):
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