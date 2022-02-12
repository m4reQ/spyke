import spyke
from spyke.ecs import components
from spyke.ecs import scene
from spyke.application import Application
from spyke.windowing import WindowSpecs
from spyke.graphics import *
from spyke.enums import *
from spyke import resources
from spyke.utils import *


class App(Application):
    def on_load(self):
        main_scene = scene.create()

        sound1 = resources.load('tests/test_sound.mp3')
        print(resources.get(sound1))

        main_scene.create_entity(
            components.TagComponent('sound1'),
        )
        scene.set_current(main_scene)

    def on_frame(self):
        pass

    def on_close(self):
        pass


if __name__ == "__main__":
    specs = WindowSpecs(1080, 720, 'TestWindow')

    app = App(specs)
    spyke.run(app)
