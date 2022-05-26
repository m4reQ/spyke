from __future__ import annotations

import logging
import queue
import typing as t

if t.TYPE_CHECKING:
    from spyke.resources.loaders import LoaderBase

_logger = logging.getLogger(__name__)
_queue: queue.Queue[LoaderBase] = queue.Queue(32)

def put_loader(loader: LoaderBase) -> None:
    _queue.put_nowait(loader)

def process() -> None:
    while not _queue.empty():
        loader = _queue.get_nowait()
        if loader.has_loading_error:
            raise loader.loading_error from RuntimeError(f'An error was encountered while loading resource {loader.resource}.') # type: ignore

        loader.join()
        try:
            loader.finish_loading()
        except Exception as e:
            raise e from RuntimeError(f'An error was encountered while trying to finalize loading of resource {loader.resource}.')
        
        loader.resource.is_loaded = True

        _logger.info('Resource %s loaded in %f seconds.', loader.resource, loader.loading_time)
