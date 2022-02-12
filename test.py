from spyke.ecs import components
from spyke.ecs import scene
from spyke import debug
from spyke import events
from spyke.application import Application
from spyke.windowing import WindowSpecs
from spyke.graphics import *
from spyke.enums import *
from spyke import resources
from spyke.utils import *
import spyke


class App(Application):
    def on_load(self):
        main_scene = scene.create()

        sound1 = resources.load('tests/test_sound.mp3')
        print(resources.get(sound1))

        main_scene.create_entity(
            components.TagComponent('sound1'),
        )

        # tex1 = resources.load('tests/test1.jpg')
        # tex2 = resources.load('tests/test2.png')
        # tex3 = resources.load('tests/test3.jpg')
        # tex4 = resources.load('tests/test3_dxt5.dds')
        # font_futuram = resources.load('tests/futuram.ttf', size=96)

        # main_scene.create_entity(
        #     components.TagComponent('texture'),
        #     components.TransformComponent(
        #         Vector3(0.0), Vector3(1.0, 1.0, 0.0), Vector3(0.0)),
        #     components.SpriteComponent(
        #         tex1, Vector2(2.0), color(1.0, 1.0, 1.0, 0.3))
        # )

        # main_scene.create_entity(
        #     components.TagComponent('texture3'),
        #     components.TransformComponent(
        #         Vector3(0.2, 0.7, 0.0), Vector3(0.3, 0.3, 0.0), Vector3(0.0, 0.0, 45.0)),
        #     components.SpriteComponent(
        #         tex3, Vector2(1.0), color(1.0, 0.0, 1.0, 0.3))
        # )

        # main_scene.create_entity(
        #     components.TagComponent('text'),
        #     components.TransformComponent(
        #         Vector3(-0.5, 0.5, 0.0), Vector3(1.0, 1.0, 0.0), Vector3(0.0)),
        #     components.TextComponent(
        #         'jebać papieża 2137', 100, font_futuram, color(1.0, 0.0, 0.0, 1.0))
        # )

        # main_scene.create_entity(
        #     components.TagComponent('text2'),
        #     components.TransformComponent(
        #         Vector3(0.4), Vector3(1.0, 1.0, 0.0), Vector3(0.0)),
        #     components.TextComponent(
        #         'TEST', 42, font_futuram, color(1.0, 1.0, 0.0, 1.0))
        # )

        # main_scene.create_entity(
        #     components.TagComponent('texture2'),
        #     components.TransformComponent(
        #         Vector3(0.5), Vector3(0.5, 0.5, 0.0), Vector3(0.0)),
        #     components.SpriteComponent(
        #         tex2, Vector2(1.0), color(1.0, 1.0, 1.0, 1.0))
        # )

        # main_scene.create_entity(
        #     components.TagComponent('single_char'),
        #     components.TransformComponent(
        #         Vector3(-0.5, -0.5, 0.0), Vector3(1.0), Vector3(0.0)),
        #     components.TextComponent(
        #         'H', 600, font_futuram, color(1.0, 1.0, 1.0, 1.0))
        # )

        # main_scene.create_entity(
        #     components.TagComponent('dds_texture'),
        #     components.TransformComponent(
        #         Vector3(-1.0, -1.0, 0.0), Vector3(1.0), Vector3(15.0),
        #     ),
        #     components.SpriteComponent(
        #         tex4, Vector2(1.0), color(1.0, 1.0, 1.0, 1.0))
        # )

        scene.set_current(main_scene)
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
