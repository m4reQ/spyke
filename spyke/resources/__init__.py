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
from spyke import debug
from spyke.exceptions import SpykeException
from .image import Image
from .font import Font

# NOTE: All functions from this module are called from main thread.
# Concurrent calls only occur through ThreadPoolExecutor.

MAX_LOADING_THREADS = 1
RESOURCE_TRY_FINALIZE_TIMEOUT = 0.01

_resources: Dict[uuid.UUID, Union[Resource, Future[Resource]]] = {}
_thread_executor: ThreadPoolExecutor = ThreadPoolExecutor(
    max_workers=MAX_LOADING_THREADS, thread_name_prefix='spyke.load.')


def _detect_resource_type(filepath: str) -> Type[Resource]:
    _, ext = path.splitext(filepath)
    ext = ext.lower().replace('.', '')

    # TODO: Add support for .dds files
    if ext in ['png', 'jpg', 'jpeg', 'bmp']:
        return Image
    if ext == 'fnt':
        return Font
    else:
        raise SpykeException(f'Unknown resource file extension: {ext}.')


def _shutdown_thread_executor() -> None:
    _thread_executor.shutdown()


def _load(id: uuid.UUID, filepath: str) -> Resource:
    _type: Type[Resource] = _detect_resource_type(filepath)

    res = _type(id, filepath)
    res.load()

    return res


def load(filepath: str) -> uuid.UUID:
    '''
    Submits loading task for resource from given file and returns its UUID.
    It automatically detects the resource type based on file extension.

    :param filepath: Path to a file containing resource data.
    '''

    if not path.exists(filepath):
        raise SpykeException(f'Resource file "{filepath}" does not exist.')

    # TODO: Consider having guard that disallows loading the same file as multiple resources

    _id = uuid.uuid4()
    res_future = _thread_executor.submit(_load, _id, filepath)
    _resources[_id] = res_future

    get.cache_clear()

    return _id


@lru_cache
def get(_id: uuid.UUID) -> Resource:
    '''
    Gets resource with given id and finalizes its loading if neccessary.

    :param _id: UUID of queried resource.
    '''

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
        _res.cleanup()

        _resources[_res.id] = _res
        get.cache_clear()

        res = _res

    return res


def unload(_id: uuid.UUID) -> None:
    if _id not in _resources:
        raise SpykeException(f'Resource with id: {_id} not found.')

    res = _resources.pop(_id)
    res.unload()
    get.cache_clear()
