import functools
import inspect
import logging
import os
import queue
import threading
import time
import typing as t
import uuid
import weakref
from concurrent import futures

from spyke import exceptions, paths, runtime
from spyke.debug.profiling import profiled
from spyke.resources import loaders, types
from spyke.resources.loaders import LoaderBase
from spyke.resources.types import *
from spyke.resources.types import ResourceBase
from spyke.utils import once

__all__ = [
    'load',
    'unload',
    'get'
] + types.__all__

MAX_PROCESS_WAIT_TIME = 0.16

T_Resource = t.TypeVar('T_Resource', bound=ResourceBase)

@once
@profiled('resources', 'initialization')
def initialize():
    if not os.path.exists(paths.SCREENSHOTS_DIRECTORY):
        os.mkdir(paths.SCREENSHOTS_DIRECTORY)
        _logger.debug('Missing screenshots directory created.')

    if not os.path.exists(paths.SHADER_SOURCES_DIRECTORY):
        raise exceptions.SpykeException('Could not find shader sources directory. This may indicate problems with installation.')

    for _loader in (_type for name, _type in inspect.getmembers(loaders, lambda x: inspect.isclass(x) and issubclass(x, LoaderBase) and not inspect.isabstract(x)) if not name.startswith('__')):
        _loaders.update({ext: _loader for ext in _loader.__supported_extensions__})
    _logger.debug('Internal resouce types loaded.')

    for _resource in (_type for name, _type in inspect.getmembers(types, lambda x: inspect.isclass(x) and issubclass(x, ResourceBase) and not inspect.isabstract(x)) if not name.startswith('__')):
        _resource_types.update({ext: _resource for ext in _resource.__supported_extensions__})
    _logger.debug('Resource loaders initialied.')

    Model.quad = _add_resource(Model.create_quad_model())
    # Image.empty = _add_resource(Image.create_empty_image())
    _logger.debug('Internal resource handles created.')

    _logger.debug('Resources module initialized.')

@profiled('resources')
def load_from_file(filepath: str) -> uuid.UUID:
    '''
    Submits loading task for resource from given file and returns its UUID.
    It automatically detects the resource type based on file extension.

    @filepath: Path to a file containing resource data.

    Raises:
        - `SpykeException` if provided filepath does not exist.
        - `SpykeException` if loader for given file extension could not be found.
        - `SpykeException` if desired resource type could not be determined.
    '''

    path = os.path.abspath(filepath)
    if not os.path.exists(path):
        raise exceptions.SpykeException(f'Cannot find resource file: {path}.')

    ext = os.path.splitext(path)[1]
    loader = _get_loader_for_extension(ext)
    resource_type = _get_resource_type_for_extension(ext)

    _id = uuid.uuid4()
    resource = resource_type(_id, filepath)
    _add_resource(resource)

    fut = _load_executor.submit(loader.load_from_file, filepath)
    fut.add_done_callback(lambda data: _finalization_queue.put_nowait(lambda: loader.finalize_loading(resource, data.result())))

    return _id

@functools.lru_cache
def get(_id: uuid.UUID, resource_type: type[T_Resource]) -> T_Resource:
    '''
    Gets proxy object to resource with given id and finalizes its loading if neccessary.

    @_id: UUID of queried resource.
    @resource_type: Type of resource we expect to return.

    Raises:
        - (DEBUG) `AssertionError` if function is called from a thread different than main.
        - `SpykeException` if resource retrieved from registry does not match requested type.
        - `SpykeException` if resource is not in registry.
    '''

    assert threading.current_thread() is threading.main_thread(), 'resource.get function can only be called from main thread.'

    if _id not in _resources:
        raise exceptions.SpykeException(f'Resource with id {_id} not found.')

    resource = _resources[_id]
    if not isinstance(resource, resource_type):
        raise exceptions.SpykeException(f'Retrieved resource\'s type does not match requested type {resource_type.__name__} (got {type(resource).__name__}).')

    return weakref.proxy(resource)

def unload(_id: uuid.UUID) -> None:
    '''
    Unloads resource with given id.
    This method ensures that all data used by resouce,
    such as graphics buffers or textures are freed and resource is
    safe to be deleted. It also automatically removes resource from
    available resources list.
    '''

    if _id not in _resources:
        _logger.warning(f'Resource with id %s not found.', _id)
        return

    resource = _resources[_id]
    if weakref.getweakrefcount(resource) != 0:
        # TODO: Create a way to remove resource references from all components
        # possibly use some resource removed event
        _logger.warning('Cannot unload resource that is still being used.')

    res = _resources.pop(_id)
    res.unload()

    _logger.debug('Resource with id %s unloaded.', _id)

def unload_all() -> None:
    '''
    Unloads all resources currently present in resource registry.
    '''

    resources = _resources.copy().values()
    for resource in resources:
        resource.unload()

def process_loading_queue() -> None:
    while not _finalization_queue.empty():
        task = _finalization_queue.get_nowait()
        task()

def _get_loader_for_extension(extension: str) -> type[LoaderBase]:
    if extension not in _loaders:
        raise exceptions.LoaderNotFoundException(extension)

    return _loaders[extension]

def _get_resource_type_for_extension(extension: str) -> type[ResourceBase]:
    _type = _resource_types[extension]
    if _type is None:
        raise exceptions.SpykeException(f'Cannot determine resource type for extension: {extension}')

    return _type

def _add_resource(resource: ResourceBase) -> uuid.UUID:
    if resource.id is not None:
        _id = resource.id
    else:
        _id = uuid.uuid4()

    resource.id = _id
    _resources[_id] = resource

    return _id

_resources: dict[uuid.UUID, ResourceBase] = {}
_loaders: dict[str, type[LoaderBase]] = {}
_resource_types: dict[str, type[ResourceBase]] = {}
_logger = logging.getLogger(__name__)
_load_executor = futures.ThreadPoolExecutor(thread_name_prefix='ResourceLoad')
_finalization_queue = queue.Queue[t.Callable[[], None]]()
