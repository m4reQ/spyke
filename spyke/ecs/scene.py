# TODO: Possibly convert this to an object held by Application class
from __future__ import annotations
from .components import AudioComponent
from .processors import *
from esper import World as Scene
from typing import Optional
import logging

_LOGGER = logging.getLogger(__name__)

_current: Optional[Scene] = None

def get_current() -> Scene:
    assert _current is not None, 'No scene is set current.'
    return _current


def set_current(scene: Scene) -> None:
    global _current
    _current = scene


def cleanup() -> None:
    '''
    Some components directly use internal objects that have to be
    cleaned up before closing the program (such as textures).
    This function cleans up all of those objects in current scene.
    '''

    if _current is None:
        return
    
    for _, audio in _current.get_component(AudioComponent):
        audio.source.delete()
    
    _LOGGER.debug('Current scene cleanup completed.')


def create() -> Scene:
    s = Scene()
    s.add_processor(TransformProcessor())
    s.add_processor(ParticleProcessor())

    return s
