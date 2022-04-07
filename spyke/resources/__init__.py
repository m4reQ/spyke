from __future__ import annotations
from spyke import utils, events, paths
from spyke.exceptions import SpykeException
from spyke.resources.loaders import Loader
from spyke.resources.types.resource import Resource
from spyke.resources.types import *
from . import loaders
from typing import Dict, Type, TypeVar
from functools import lru_cache
import os
import threading
import uuid
import weakref
import inspect
import logging

T_Resource = TypeVar('T_Resource', bound=Resource)

_loaders: Dict[str, Type[Loader]] = dict()
_resources: Dict[uuid.UUID, Resource] = dict()

_LOGGER = logging.getLogger(__name__)

def _register_loaders() -> None:
    def _is_loader(obj) -> bool:
        return inspect.isclass(obj) and \
            not inspect.isabstract(obj) and \
            issubclass(obj, Loader)

    modules = utils.get_submodules(loaders)
    _classes = list()

    for module in modules:
        _classes.extend([x[1] for x in inspect.getmembers(module, _is_loader)])
    
    registered_count = 0
    for _class in _classes:
        if not _class.__name__.endswith('Loader'):
            _LOGGER.warning('Loader class names should always end with "Loader" suffix.')

        for extension in _class.__extensions__:
            _loaders[extension] = _class
            registered_count += 1
            _LOGGER.debug('Loader %s registered for file extension: %s.', _class.__name__, extension)
    
    _LOGGER.debug('Registered %d loaders.', registered_count)

def _get_loader(restype: str) -> Type[Loader]:
    # TODO: Don't throw exception here. Better just quit loading resource and use Resource.invalid
    assert restype in _loaders, f'Could not find loader for resource type: {restype}'

    return _loaders[restype]

def _is_resource_from_filepath_loaded(filepath: str) -> bool:
    for res in _resources.values():
        if res.filepath == filepath:
            return True

    return False

def _resource_loaded_callback(event: events.ResourceLoadedEvent) -> None:
    loader: Loader = event.loader
    loader.finalize()

def _init() -> None:
    _register_loaders()
    events.register(_resource_loaded_callback, events.ResourceLoadedEvent, priority=-1, consume=True)

    if not os.path.exists(paths.SCREENSHOTS_DIRECTORY):
        os.mkdir(paths.SCREENSHOTS_DIRECTORY)
        _LOGGER.debug('Missing screenshots directory created.')
    
    if not os.path.exists(paths.SHADER_SOURCES_DIRECTORY):
        raise SpykeException('Could not find shader sources directory. This may indicate problems with installation.')
    
    _LOGGER.debug('Resources module initialized.')

def load(filepath: str, **resource_settings) -> uuid.UUID:
    '''
    Submits loading task for resource from given file and returns its UUID.
    It automatically detects the resource type based on file extension.

    @filepath: Path to a file containing resource data.

    Raises:
        - (DEBUG) `AssertionError` if provided filepath does not exist.
    '''

    assert os.path.exists(filepath), f'Resource file "{filepath}" does not exist.'

    if _is_resource_from_filepath_loaded(filepath):
        _LOGGER.warning('Resource from file "%s" is already loaded. Avoid loading the same resource multiple times.', filepath)

    _id = uuid.uuid4()

    loader_class = _get_loader(utils.get_extension_name(filepath))
    resource = loader_class.__restype__(_id, filepath)
    loader = loader_class(resource)

    _resources[_id] = resource
    loader.start()

    return _id

@lru_cache
def get(_id: uuid.UUID, resource_type: Type[T_Resource]) -> T_Resource:
    '''
    Gets proxy object to resource with given id and finalizes its loading if neccessary.

    @_id: UUID of queried resource.
    @resource_type: Type of resource we expect to return.

    Raises:
        - (DEBUG) `AssertionError` if function is called from a thread different than main.
        - (DEBUG) `AssertionError` if resource retrieved from registry does not match requested type.
        - `SpykeException` if resource is not in registry.
    '''

    assert threading.current_thread() is threading.main_thread(), 'resource.get function can only be called from main thread.'

    if _id not in _resources:
        raise SpykeException(f'Resource with id {_id} not found.')
    
    resource = _resources[_id]
    assert isinstance(resource, resource_type), f'Retrieved resource\'s type does not match requested type {resource_type.__name__} (got {type(resource).__name__}).'

    return weakref.proxy(resource) #type: ignore

def _unload(_id: uuid.UUID) -> None:
    # cannot use dict.pop here as it would change dictionary
    # size and later cause error while iterating over it
    res = _resources[_id]
    res.unload()

    _LOGGER.info('Resource (%s) unloaded.', res)

def unload(_id: uuid.UUID) -> None:
    '''
    Unloads resource given by its id. This method
    ensures that all data used by resouce such as graphics buffers or textures
    are freed and resource is safe to delete.
    It also automatically removes resource from available resources list.
    '''

    if _id not in _resources:
        _LOGGER.warning(f'Resource with id %s not found.', _id)
        return
    
    if _id in _resources:
        resource = _resources[_id]
        if weakref.getweakrefcount(resource) != 0:
            # TODO: Create a way to remove resource references from all components
            # possibly use some resource removed event
            _LOGGER.warning(f'Resource (%s) is already in use. Unloading resources that are still being used by components may lead to rendering errors or even crashes.', resource)

    _unload(_id)
    get.cache_clear()

def unload_all() -> None:
    for _id in _resources:
        _unload(_id)
    
    _resources.clear()
    
    _LOGGER.debug('All resources unloaded.')