import typing as t

from esper import World as Scene

from .processors import *

_current: t.Optional[Scene] = None

def get_current() -> Scene:
    assert _current is not None, 'No scene is set current.'
    return _current

def set_current(scene: Scene) -> None:
    global _current
    _current = scene

def create() -> Scene:
    s = Scene()
    s.add_processor(TransformProcessor())
    s.add_processor(ParticleProcessor())

    return s
