import os
import threading
import uuid
import weakref
import inspect
import logging
import functools
import typing as t

from spyke import utils, paths
from spyke.exceptions import SpykeException
from spyke.resources.loaders import LoaderBase
from spyke.resources.types import ResourceBase
from spyke.resources import types
from spyke.resources import loaders

from spyke.resources.types import *

__all__ = [
    'load',
    'unload',
    'get'
] + types.__all__

T_Resource = t.TypeVar('T_Resource', bound=ResourceBase)

_loaders: t.Dict[str, t.Type[LoaderBase]] = {}
_resources: t.Dict[uuid.UUID, ResourceBase] = {}
_resource_types: t.Dict[str, t.Type[ResourceBase]] = {}

_logger = logging.getLogger(__name__)

def load(filepath: str) -> uuid.UUID:
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
        raise SpykeException(f'Cannot find resource file: {path}.')

    ext = os.path.splitext(path)[1]

    loader_type = _get_loader_for_extension(ext)
    if loader_type is None:
        raise SpykeException(f'Cannot load resource with extension: {ext}')

    resource_type = _get_resource_type_for_extension(ext)
    if resource_type is None:
        raise SpykeException(f'Cannot determine resource type for extension: {ext}')

    _id = uuid.uuid4()
    resource = resource_type(_id, filepath)
    loader = loader_type(resource)

    _add_resource(resource)
    
    loader.start()

    return _id

@functools.lru_cache
def get(_id: uuid.UUID, resource_type: t.Type[T_Resource]) -> T_Resource:
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
        raise SpykeException(f'Resource with id {_id} not found.')

    resource = _resources[_id]
    if not isinstance(resource, resource_type):
        raise SpykeException(f'Retrieved resource\'s type does not match requested type {resource_type.__name__} (got {type(resource).__name__}).')

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
    resources = _resources.copy().values()
    for resource in resources:
        resource.unload()

def _register_resource_types() -> None:
    def _is_resource_type(obj: object) -> bool:
        return inspect.isclass(obj) \
            and not inspect.isabstract(obj) \
            and issubclass(obj, ResourceBase) # type: ignore

    modules = utils.get_submodules(types)

    for module in modules:
        classes = [x[1] for x in inspect.getmembers(module, _is_resource_type)]
        for _class in classes:
            for ext in _class.get_suitable_extensions():
                _resource_types[ext] = _class
                _logger.debug('Resource type %s registered for file extension: %s.', _class.__name__, ext)

def _register_loaders() -> None:
    def _is_loader(obj) -> bool:
        return inspect.isclass(obj) \
            and not inspect.isabstract(obj) \
            and issubclass(obj, LoaderBase) # type: ignore

    modules = utils.get_submodules(loaders)

    for module in modules:
        classes = [x[1] for x in inspect.getmembers(module, _is_loader)]
        for _class in classes:
            for ext in _class.get_suitable_extensions():
                _loaders[ext] = _class
                _logger.debug('Loader %s registered for file extension: %s.', _class.__name__, ext)

def _get_loader_for_extension(extension: str) -> t.Optional[t.Type[LoaderBase]]:
    return _loaders[extension]

def _get_resource_type_for_extension(extension: str) -> t.Optional[t.Type[ResourceBase]]:
    return _resource_types[extension]

def _add_resource(resource: ResourceBase) -> uuid.UUID:
    if resource.id is not None:
        _id = resource.id
    else:
        _id = uuid.uuid4()
        
    resource.id = _id
    _resources[_id] = resource
    
    return _id

def init():
    _register_loaders()
    _register_resource_types()

    if not os.path.exists(paths.SCREENSHOTS_DIRECTORY):
        os.mkdir(paths.SCREENSHOTS_DIRECTORY)
        _logger.debug('Missing screenshots directory created.')

    if not os.path.exists(paths.SHADER_SOURCES_DIRECTORY):
        raise SpykeException('Could not find shader sources directory. This may indicate problems with installation.')

    Model.quad = _add_resource(Model.create_quad_model())
    Image.empty = _add_resource(Image.create_empty_image())
    _logger.debug('Internal resource handles created.')
    
    _logger.debug('Resources module initialized.')
