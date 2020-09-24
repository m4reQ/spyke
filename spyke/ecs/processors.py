from .esper import Processor
from .components import TransformComponent, TextComponent
from ..graphics import Renderer

class RenderingProcessor(Processor):
    def process(self, renderer: Renderer):
        renderer.BeginScene()

        for _, sprite, transform in self.world.get_components(SpriteComponent, TransformComponent):
            renderer.RenderQuad(transform.Transform, sprite.Color, sprite.Texture, sprite.TilingFactor)
        
        for _, text, transform in self.world.get_component(TextComponent, TransformComponent):
            renderer.RenderText(transform.Position, text.Color, text.Font, text.Size, text.Text)
        
        renderer.EndScene()

class TransformProcessor(Processor):
    def process(self):
        for _, transform in self.world.get_component(TransformComponent):
            if transform.ShouldRecalculate:
                transform.Recalculate()