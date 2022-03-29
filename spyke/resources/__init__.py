from __future__ import annotations
from spyke import debug, utils
from spyke.exceptions import SpykeException
from spyke.resources.loaders import Loader
from spyke.resources.resource import Resource
from spyke.resources.types import *
from . import loaders
from typing import Dict, Type
from functools import lru_cache
from os import path
import threading
import uuid
import weakref
import inspect

# NOTE: All functions from this module are called from main thread.
# Concurrent calls only occur through ThreadPoolExecutor.

MAX_LOADING_TASKS = 8

_loaders: Dict[str, Type[Loader]] = dict()
_resources: Dict[uuid.UUID, Resource] = dict()
_loading_tasks: Dict[uuid.UUID, Loader] = dict()
_loading_semaphore: threading.BoundedSemaphore = threading.BoundedSemaphore(MAX_LOADING_TASKS)

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
            debug.log_warning('Loader class names should always end with "Loader" suffix.')

        for extension in _class.__extensions__:
            _loaders[extension] = _class
            registered_count += 1
            debug.log_info(f'Loader {_class.__name__} registered for file extension: {extension}.')
    
    debug.log_info(f'Registered {registered_count} loaders.')

_register_loaders()

def _get_loader(restype: str) -> Type[Loader]:
    # TODO: Don't throw exception here. Better just quit loading resource and use Resource.invalid
    assert restype in _loaders, f'Could not find loader for resource type: {restype}'

    return _loaders[restype]

def _is_resource_from_filepath_loaded(filepath: str) -> bool:
    for res in _resources.values():
        if res.filepath == filepath:
            return True

    return False

##########################################
# CHUJ
# _finalize is not guaranteed to be called within the main
# thread, so we cannot use any OpenGL functions there
# Find another way to get around this limitation possibly using
# some kind of finalization token
##########################################


def _finalize(_id: uuid.UUID) -> None:
    '''
    Finalizes loading of resource with given id and registers created object in resources
    registry.

    @_id: UUID of requested resource loading task.
    '''
    
    loader = _loading_tasks[_id]
    loader.wait()
    res = loader.finalize()
    _resources[_id] = res
    get.cache_clear()

def load(filepath: str, **resource_settings) -> uuid.UUID:
    '''
    Submits loading task for resource from given file and returns its UUID.
    It automatically detects the resource type based on file extension.

    @filepath: Path to a file containing resource data.

    Raises:
        - (DEBUG) `AssertionError` if provided filepath does not exist.
    '''

    assert path.exists(filepath), f'Resource file "{filepath}" does not exist.'

    if _is_resource_from_filepath_loaded(filepath):
        debug.log_warning(f'Resource from file "{filepath}" is already loaded. Avoid loading the same resource multiple times.')

    _id = uuid.uuid4()
    ext = utils.get_extension_name(filepath)
    loader = _get_loader(ext)(_id, filepath)

    _loading_semaphore.acquire()
    _loading_tasks[_id] = loader
    loader.start()

    return _id

@lru_cache
def get(_id: uuid.UUID) -> Resource:
    '''
    Gets proxy object to resource with given id and finalizes its loading if neccessary.

    @_id: UUID of queried resource.

    Raises:
        - (DEBUG) `AssertionError` if function is called from a thread different than main.
        - `SpykeException` if resource is not in registry and is not in loading queue.
    '''

    assert threading.current_thread() is threading.main_thread(), 'resource.get function can only be called from main thread.'
    
    if _id not in _resources:
        if _id not in _loading_tasks:
            raise SpykeException(f'Resource with id {_id} not found.')
        
        _finalize(_id)
    
    return weakref.proxy(_resources[_id])

def _unload(_id: uuid.UUID) -> None:
    if _id in _resources:
        res = _resources[_id]
        res.unload()
        debug.log_info(f'Resource with id {_id} unloaded.')

    # we have to wait for loading task to finish
    # as we cannot kill the thread
    loader = _loading_tasks.pop(_id)
    loader.wait()

    debug.log_info('Resource loading cancelled.')

def unload(_id: uuid.UUID) -> None:
    '''
    Unloads resource given by its id. This method
    ensures that all data used by resouce such as graphics buffers or textures
    are freed and resource is safe to delete.
    It also automatically removes resource from available resources list.
    '''

    if _id not in _resources and _id not in _loading_tasks:
        debug.log_warning(f'Resource with id: {_id} not found.')
        return
    
    if _id in _resources:
        if weakref.getweakrefcount(_resources[_id]) != 0:
            # TODO: Create a way to remove resource references from all components
            # possibly use some resource removed event
            debug.log_warning(f'Resource ({_resources[_id]}) is already in use. Unloading resources that are still being used by components may lead to rendering errors or even crashes.')

    _unload(_id)
    get.cache_clear()

def unload_all() -> None:
    for _id in _resources:
        _unload(_id)
    
    _resources.clear()
    
    debug.log_info('All resources unloaded.')