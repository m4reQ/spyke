from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from .resource import Resource
    from typing import Dict, Type, Union

from concurrent.futures import ThreadPoolExecutor, Future
import threading
import uuid
from functools import lru_cache
from os import path
import weakref
from spyke import debug
from spyke.exceptions import SpykeException
from .image import Image
from .font import Font

# NOTE: All functions from this module are called from main thread.
# Concurrent calls only occur through ThreadPoolExecutor.

MAX_LOADING_THREADS = 4

_resources: Dict[uuid.UUID, Union[Resource, Future[Resource]]] = {}
_thread_executor: ThreadPoolExecutor = ThreadPoolExecutor(
    max_workers=MAX_LOADING_THREADS, thread_name_prefix='spyke.load.')


def _detect_resource_type(filepath: str) -> Type[Resource]:
    _, ext = path.splitext(filepath)
    ext = ext.lower().replace('.', '')

    # TODO: Add support for .dds files
    # TODO: Move this to somewhere in loaders
    if ext in ['png', 'jpg', 'jpeg', 'bmp', 'dds']:
        return Image
    if ext == 'ttf':
        return Font
    else:
        raise SpykeException(f'Unknown resource file extension: {ext}.')


def _shutdown_thread_executor() -> None:
    _thread_executor.shutdown()


def _load(id: uuid.UUID, filepath: str, **resource_settings) -> Resource:
    _type: Type[Resource] = _detect_resource_type(filepath)

    res = _type(id, filepath)
    res.load(**resource_settings)

    return res


def load(filepath: str, **resource_settings) -> uuid.UUID:
    '''
    Submits loading task for resource from given file and returns its UUID.
    It automatically detects the resource type based on file extension.

    :param filepath: Path to a file containing resource data.
    '''

    if not path.exists(filepath):
        raise SpykeException(f'Resource file "{filepath}" does not exist.')

    # TODO: Consider having guard that disallows loading the same file as multiple resources

    _id = uuid.uuid4()
    res_future = _thread_executor.submit(
        _load, _id, filepath, **resource_settings)
    _resources[_id] = res_future

    get.cache_clear()

    return _id


@lru_cache
def get(_id: uuid.UUID) -> Resource:
    '''
    Gets proxy object to resource with given id and finalizes its loading if neccessary.

    :param _id: UUID of queried resource.
    '''

    # TODO: Handle resource not found in safer way instead of throwing an exception
    # TODO: Convert below check to assertion
    if __debug__:
        if threading.current_thread() is not threading.main_thread():
            raise SpykeException(
                'resource.get function can only be called from main thread.')

    if _id not in _resources:
        raise SpykeException(f'Resource with id: {_id} not found.')

    res = _resources[_id]
    if isinstance(res, Future):
        _res = res.result()
        _res.finalize()

        _resources[_id] = _res
        get.cache_clear()

    return weakref.proxy(_resources[_id])


def unload(_id: uuid.UUID) -> None:
    if _id not in _resources:
        raise SpykeException(f'Resource with id: {_id} not found.')

    res = _resources.pop(_id)
    # TODO: Handle this specific case more accurately
    if isinstance(res, Future):
        debug.log_warning(
            'Tried to unload resource that has not been yet loaded.')
        return

    if weakref.getweakrefcount(res) != 0:
        debug.log_warning(
            f'Resource ({res}) is already in use. To unload resource make sure that no components are using it anymore.')
        return

    res.unload()
    get.cache_clear()
