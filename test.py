from spyke.ecs import components
from spyke import debug
from spyke import events
from spyke.application import Application
from spyke.graphics import WindowSpecs
from spyke.graphics import *
from spyke.enums import *
from spyke import resourceManager as ResourceManager
from spyke.utils import *
import spyke


class App(Application):
    def on_load(self):
        ResourceManager.SetSceneCurrent(ResourceManager.CreateScene('Test'))
        ResourceManager.CreateTexture('tests/test1.jpg', 'tex1')
        ResourceManager.CreateTexture('tests/test2.png', 'tex2')
        ResourceManager.CreateTexture('tests/test3.jpg', 'tex3')
        ResourceManager.CreateFont(
            'tests/ArialNative.fnt', 'tests/ArialNative.png', 'arial')

        ResourceManager.GetCurrentScene().CreateEntity(
            components.TagComponent('texture'),
            components.TransformComponent(
                Vector3(0.0), Vector3(1.0, 1.0, 0.0), Vector3(0.0)),
            components.SpriteComponent(
                'tex1', Vector2(1.0), color(1.0, 1.0, 1.0, 0.3))
        )

        ResourceManager.GetCurrentScene().CreateEntity(
            components.TagComponent('texture3'),
            components.TransformComponent(
                Vector3(0.2, 0.7, 0.0), Vector3(0.3, 0.3, 0.0), Vector3(0.0)),
            components.SpriteComponent(
                'tex3', Vector2(1.0), color(1.0, 0.0, 1.0, 0.3))
        )

        ResourceManager.GetCurrentScene().CreateEntity(
            components.TagComponent('text'),
            components.TransformComponent(
                Vector3(0.0), Vector3(1.0, 1.0, 0.0), Vector3(0.0)),
            components.TextComponent(
                'TEST', 80, 'arial', color(1.0, 0.0, 0.0, 1.0))
        )

        ResourceManager.GetCurrentScene().CreateEntity(
            components.TagComponent('text2'),
            components.TransformComponent(
                Vector3(0.4), Vector3(1.0, 1.0, 0.0), Vector3(0.0)),
            components.TextComponent(
                'TEST2', 42, 'arial', color(1.0, 1.0, 0.0, 1.0))
        )

        ResourceManager.GetCurrentScene().CreateEntity(
            components.TagComponent('texture2'),
            components.TransformComponent(
                Vector3(0.5), Vector3(0.5, 0.5, 0.0), Vector3(0.0)),
            components.SpriteComponent(
                'tex2', Vector2(1.0), color(1.0, 1.0, 1.0, 1.0))
        )
        # ResourceManager.GetCurrentScene().CreateEntity(
        # 	components.TagComponent('font_texture'),
        # 	components.TransformComponent(Vector3(0.3), Vector3(1.0, 1.0, 0.0), Vector3(0.0)),
        # 	components.SpriteComponent('font_arial_texture', Vector2(1.0), color(1.0, 0.0, 0.0, 1.0))
        # )
        # LoadScene("tests/newScene.scn")

        # self.ent4 = EntityManager.CreateEntity("Particles")
        # self.particleSystem1 = ParticleSystemComponent(Vector2(0.5, 0.5), 3.0, 50)
        # self.particleSystem1.colorBegin = color(1.0, 0.0, 1.0, 1.0)
        # self.particleSystem1.colorEnd = color(0.0, 1.0, 1.0, 1.0)
        # self.particleSystem1.sizeBegin = Vector2(0.25, 0.25)
        # self.particleSystem1.sizeEnd = Vector2(0.1, 0.1)
        # self.particleSystem1.velocity = Vector2(0.1, 0.3)
        # self.particleSystem1.rotationVelocity = 0.0
        # self.particleSystem1.randomizeMovement = True
        # self.particleSystem1.fadeOut = True
        # self.particleSystem1.texHandle = "tests/test1.jpg"
        # ecs.CurrentScene.AddComponent(self.ent4, self.particleSystem1)

        # ResourceManager.LoadScene("tests/scene.scn")

        # events.register_method(
        #     self.move_camera, events.KeyDownEvent, priority=0)

    def move_camera(self, e: events.KeyDownEvent):
        frametime = self.frame_stats.frametime

        if e.key == Keys.KeyW:
            self.camera.Move(Vector3(0.0, 0.01, 0.0), frametime)
        elif e.key == Keys.KeyS:
            self.camera.Move(Vector3(0.0, -0.01, 0.0), frametime)
        elif e.key == Keys.KeyA:
            self.camera.Move(Vector3(-0.01, 0.0, 0.0), frametime)
        elif e.key == Keys.KeyD:
            self.camera.Move(Vector3(0.01, 0.0, 0.0), frametime)
        else:
            return

        debug.log_info('Camera moved.')

        debug.get_gl_error()

    def on_frame(self):
        pass

    def on_close(self):
        pass


if __name__ == "__main__":
    specs = WindowSpecs(1080, 720, 'TestWindow')
    specs.samples = 2
    specs.vsync = True

    app = App(specs)
    spyke.run(app, run_editor=False)
