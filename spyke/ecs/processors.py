from .esper import Processor
from .components import *
from spyke.utils import lerp_float, lerp_vector


class TransformProcessor(Processor):
    def Process(self, *args, **kwargs):
        for _, transform in self.scene.GetComponent(TransformComponent):
            if transform.should_recalculate:
                transform.recalculate()

        for _, (camera, transform) in self.scene.GetComponents(CameraComponent, TransformComponent):
            if camera.should_recalculate:
                camera.recalculate(transform.matrix)


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
                    particle.color = lerp_vector(
                        particle.life / particleComponent.duration, particleComponent.colorEnd, particleComponent.colorBegin)

                if particleComponent.fadeOut:
                    particle.color.w = lerp_float(
                        particle.life / particleComponent.duration, 0.0, 1.0)

                if particleComponent.sizeChange:
                    particle.size = lerp_vector(
                        particle.life / particleComponent.duration, particleComponent.sizeEnd, particleComponent.sizeBegin)

                if particle.life < 0.0:
                    particle.isAlive = False
