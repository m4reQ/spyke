# TODO: Possibly convert this to an object held by Application class

from esper import World as Scene
from spyke.exceptions import SpykeException
from .processors import *

_current: Scene = None


def get_current() -> Scene:
    if not _current:
        raise SpykeException('No scene is set current.')

    return _current


def set_current(scene: Scene) -> None:
    global _current
    _current = scene


def create() -> Scene:
    s = Scene()
    s.add_processor(TransformProcessor())
    s.add_processor(ParticleProcessor())
    s.add_processor(AudioProcessor())

    return s
