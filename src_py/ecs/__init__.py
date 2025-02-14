from spyke.ecs.scene import Scene
from spyke.ecs.components.component import Component
from spyke.ecs.components.tag import TagComponent
from spyke.ecs.components.sprite import SpriteComponent
from spyke.ecs.components.text import TextComponent
from spyke.ecs.components.transform import TransformComponent

__all__ = (
    'set_current_scene',
    'get_current_scene',
    'Component',
    'TagComponent',
    'SpriteComponent',
    'TextComponent',
    'TransformComponent',
    'Scene')

# TODO: We can further increase speed of `get_components` by assigning
# each component an entity id for which it is registered. It would remove second
# iteration over types in `get_components`.

def set_current_scene(scene: Scene) -> None:
    '''
    Sets given scene "current" so it can be later retrieved from
    module-level using `get_current` function.

    @scene: The scene to be set as current.
    '''

    global _current_scene
    _current_scene = scene

def get_current_scene() -> Scene:
    '''
    Returns current global scene. If scene was not set this
    function will raise exception.
    '''

    if _current_scene is None:
        raise RuntimeError('No scene is set current.')

    return _current_scene

_current_scene: Scene | None = None
