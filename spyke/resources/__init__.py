from __future__ import annotations
import typing


if typing.TYPE_CHECKING:
    from .resource import Resource
    from typing import Dict, Type, Union

from spyke import debug
from spyke.exceptions import SpykeException
from .image import Image
from .font import Font
from concurrent.futures import ThreadPoolExecutor, Future
import threading
import uuid
from functools import lru_cache
from os import path
import weakref
from spyke import loaders
from spyke.exceptions import SpykeException
from .image import Image
from .font import Font
from .sound import Sound

# NOTE: All functions from this module are called from main thread.
# Concurrent calls only occur through ThreadPoolExecutor.

_resources: Dict[uuid.UUID, Union[Resource, Future[Resource]]] = {}
_thread_executor: ThreadPoolExecutor = ThreadPoolExecutor(
    max_workers=None, thread_name_prefix='spyke.load.')


def _detect_resource_type(filepath: str) -> Type[Resource]:
    _, ext = path.splitext(filepath)
    ext = ext.lower().replace('.', '')

    # TODO: Move this to somewhere in loaders
    if ext in ['png', 'jpg', 'jpeg', 'dds']:
        return Image
    elif ext == 'ttf':
        return Font
    elif ext in ['mp3', 'wav']:
        return Sound
    
    raise SpykeException(f'Unknown resource file extension: {ext}.')


def _load(id: uuid.UUID, filepath: str, **resource_settings) -> Resource:
    _type: Type[Resource] = _detect_resource_type(filepath)

    res = _type(id, filepath)
    res.load(**resource_settings)

    return res


def _is_resource_from_filepath_loaded(filepath: str) -> bool:
    for res in _resources.values():
        if isinstance(res, Future):
            continue

        if res.filepath == filepath:
            return True

    return False


def load(filepath: str, **resource_settings) -> uuid.UUID:
    '''
    Submits loading task for resource from given file and returns its UUID.
    It automatically detects the resource type based on file extension.

    :param filepath: Path to a file containing resource data.
    '''

    assert path.exists(filepath), f'Resource file "{filepath}" does not exist.'

    _, ext = path.splitext(filepath)
    ext = ext.replace('.', '').upper()

    assert loaders.has_loader(ext), f'Cannot load resource with extension: {ext}'

    if _is_resource_from_filepath_loaded(filepath):
        debug.log_warning(f'Resource from file "{filepath}" is already loaded. Avoid loading the same resource multiple times.')

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
    assert threading.current_thread() is threading.main_thread(), 'resource.get function can only be called from main thread.'
    assert _id in _resources, f'Resource with id: {_id} not found.'

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
        debug.log_warning('Tried to unload resource that has not been yet loaded.')
        return

    if weakref.getweakrefcount(res) != 0:
        debug.log_warning(f'Resource ({res}) is already in use. To unload resource make sure that no components are using it anymore.')
        return

    res.unload()
    get.cache_clear()
