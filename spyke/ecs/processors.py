import esper
from .components import *
from spyke.utils import lerp_float, lerp_vector

class TransformProcessor(esper.Processor):
    def process(self, *args, **kwargs):
        for _, transform in self.world.get_component(TransformComponent):
            if transform.should_recalculate:
                transform.recalculate()

        for _, (camera, transform) in self.world.get_components(CameraComponent, TransformComponent):
            if camera.should_recalculate:
                camera.recalculate(transform.matrix)

class AudioProcessor(esper.Processor):
    def process(self, *args, **kwargs):
        for _, audio in self.world.get_component(AudioComponent):
            state = audio.Handle.GetState()


class ParticleProcessor(esper.Processor):
    def process(self, dt: float):
        for _, particleComponent in self.world.get_component(ParticleSystemComponent):
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
