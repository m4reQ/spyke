from .esper import Processor
from .components import *
from ..graphics import Renderer, GLCommand, OrthographicCamera
from ..enums import ClearMask

class RenderingProcessor(Processor):
    def __init__(self, renderer: Renderer, camera: OrthographicCamera):
        self.__renderer = renderer
        self.__camera = camera

    def process(self):
        GLCommand.Clear(ClearMask.ColorBufferBit | ClearMask.DepthBufferBit)
        
        self.__renderer.BeginScene(self.__camera.viewProjectionMatrix)

        for _, (sprite, transform, color) in self.world.get_components(SpriteComponent, TransformComponent, ColorComponent):
            self.__renderer.RenderQuad(transform.Matrix, tuple(color), sprite.TextureHandle, sprite.TilingFactor)
        
        for _, (text, transform, color) in self.world.get_components(TextComponent, TransformComponent, ColorComponent):
            self.__renderer.RenderText(transform.Position, tuple(color), text.Font, text.Size, text.Text)
        
        self.__renderer.EndScene()

class TransformProcessor(Processor):
    def process(self):
        for _, transform in self.world.get_component(TransformComponent):
            if transform.ShouldRecalculate:
                transform.Recalculate()