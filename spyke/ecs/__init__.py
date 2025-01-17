from __future__ import annotations

import abc
import dataclasses
import functools
import typing as t
from collections import defaultdict

# TODO: We can further increase speed of `get_components` by assigning
# each component an entity id for which it is registered. It would remove second
# iteration over types in `get_components`.

@dataclasses.dataclass(eq=False)
class Component(abc.ABC):
    pass

class Processor(abc.ABC):
    @abc.abstractmethod
    def process(self, scene: Scene, *args: t.Any, **kwargs: t.Any) -> None:
        pass

ComponentType = t.TypeVar('ComponentType', bound=Component)
ComponentTypes = t.TypeVarTuple('ComponentTypes')

class Scene:
    def __init__(self, name: str='') -> None:
        self.name = name

        self._components_by_type = defaultdict[type[Component], set[Component]](set)
        self._components_by_entity = defaultdict[int, dict[type[Component], Component]](dict)
        self._entities_by_components = defaultdict[type[Component], set[int]](set)
        self._to_remove = set[int]()
        self._next_entity_id = 0
        self._processors: list[Processor] = []
        self._current_camera_entity: int = -1

    def create_entity(self, *components: Component) -> int:
        '''
        Creates new entity with provided components and returns its id.

        @components: List of components that should be added to the newly created entity.
        '''

        _id = self._next_entity_id
        self._next_entity_id += 1

        for comp in components:
            self.add_component(_id, comp)

        self._clear_caches()

        return _id

    def add_component(self, entity: int, component: Component) -> None:
        '''
        Adds new component to the given entity. If the entity already has
        component of that type this function does nothing.

        @entity: Id of an entity to which to add the component.
        @component: A component that will be added.
        '''

        self._components_by_type[type(component)].add(component)
        self._entities_by_components[type(component)].add(entity)
        self._components_by_entity[entity][type(component)] = component

        self._clear_caches()

    def has_component(self, entity: int, component_type: type[Component]) -> bool:
        entities = self._entities_by_components.get(component_type, None)
        if entities is not None:
            return entity in entities

        return False

    def remove_entity(self, entity: int, immediate: bool = False) -> None:
        '''
        Flags entity as enqueued to removal. This means it will
        be removed at the start of next `process` call (before processors are
        ran). If the `immediate` parameter is set to True the entity will be deleted
        immediately. If the entity is already flagged for deletion this funcition does
        nothing. NOTE: Neither this function nor functions that are called later check if
        provided entity exists. If this is not the case an exception
        could be thrown later at some point.

        @entity: Entity that should be removed.
        '''

        if immediate:
            self._remove_entity(entity)
        else:
            self._to_remove.add(entity)

    def remove_component(self, entity: int, _type: type[Component]) -> None:
        '''
        Removes component of given type from the entity. If the entity
        does not have component of given type this function does nothing.

        @entity: Id of the entity from which to remove the component.
        @_type: Type of the component that should be removed.
        '''

        self._entities_by_components[_type].discard(entity)

        entity_component_store = self._components_by_entity[entity]
        if comp := entity_component_store.get(_type, None):
            del entity_component_store[_type]
            self._components_by_type[_type].remove(comp)

        self._clear_caches()

    def add_processor(self, processor: Processor, priority: int = 0) -> None:
        '''
        Registers new processor to the scene. The `priority` is used
        to determine the order in which processors should run.
        NOTE: It is discouraged to register multiple processors of the
        same type as that may cause collisions.

        @processor: A processor instance to be registered.
        '''

        self._processors.append(processor)
        self._processors.sort(key=lambda x: priority, reverse=True)

    def remove_processor(self, _type: type[Processor]) -> None:
        '''
        Removes processor of given type. If there is no processor
        that's type matches the provided one this function does nothing.

        @_type: Type of the processor to be removed.
        '''

        proc = next((x for x in self._processors if isinstance(x, _type)), None)
        if proc is None:
            return

        self._processors.remove(proc)

    def get_current_camera_entity(self) -> int:
        return self._current_camera_entity

    def set_current_camera_entity(self, entity: int) -> None:
        self._current_camera_entity = entity

    def get_entities(self) -> t.KeysView[int]:
        return self._components_by_entity.keys()

    def process(self, *args: t.Any, **kwargs: t.Any) -> None:
        '''
        Calls `process` on every registered processor with provided arguments.
        '''

        for entity in self._to_remove:
            self._remove_entity(entity)

        for processor in self._processors:
            processor.process(self, *args, **kwargs)

    @functools.lru_cache()
    def get_components(self, *types: *ComponentTypes) -> list[tuple[int, tuple[*ComponentTypes]]]:
        '''
        Retrieves all entities that have components of given types. The returned query
        is in form of (entity, components generator). The second value will always be of length
        of number of types that were given.

        @types: Types of components that are required for entity to have.
        '''

        result = list[tuple[int, tuple[*ComponentTypes]]]()
        for entity in set.intersection(*(self._entities_by_components[x] for x in types)):
            entity_component_store = self._components_by_entity[entity]
            entity_components = tuple(
                entity_component_store[_type]
                for _type in types
                if _type in entity_component_store)
            result.append((entity, entity_components))

        return result

    @functools.lru_cache()
    def get_component(self, _type: type[ComponentType]) -> set[ComponentType]:
        '''
        Returns set of all components of given type.
        Returns empty set if there are no components of the given type.

        @_type: Type of the component to retrieve.
        '''

        return self._components_by_type.get(_type, set()) # type: ignore[return-value]

    def get_component_for_entity(self, entity: int, _type: type[ComponentType]) -> ComponentType:
        component = self._components_by_entity[entity][_type]
        assert isinstance(component, _type)

        return component

    @functools.lru_cache()
    def get_components_for_entity(self, entity: int) -> t.ValuesView[Component]:
        '''
        Returns all components that belong to given entity.
        Returns empty set if entity with given id doesn't exits.

        @entity: Entity id for which components to retrieve.
        '''

        return self._components_by_entity.get(entity, dict()).values()

    def _remove_entity(self, entity: int) -> None:
        for comp_type, comp in self._components_by_entity[entity].items():
            self._components_by_type[comp_type].remove(comp)
            self._entities_by_components[comp_type].remove(entity)

        del self._components_by_entity[entity]

    def _clear_caches(self) -> None:
        self.get_component.cache_clear()
        self.get_components.cache_clear()
        self.get_components_for_entity.cache_clear()

def set_current(scene: Scene) -> None:
    '''
    Sets given scene "current" so it can be later retrieved from
    module-level using `get_current` function.

    @scene: The scene to be set as current.
    '''

    global _current_scene
    _current_scene = scene

def get_current() -> Scene:
    '''
    Returns current global scene. If scene was not set this
    function will raise exception.
    '''

    if _current_scene is None:
        raise RuntimeError('No scene is set current.')

    return _current_scene

_current_scene: Scene | None = None
