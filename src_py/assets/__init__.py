import logging
import os
import queue
import time
import typing as t
import uuid
from concurrent import futures

from spyke import debug, events
from spyke.scheduler import Scheduler

from .asset import Asset, AssetConfig, AssetSource
from .image import Image, ImageConfig, ImageLoadData
from .model import Model, ModelLoadData

__all__ = (
    'load_from_file',
    'load_from_data',
    'load_from_file_immediate',
    'add_asset',
    'get',
    'get_or_empty',
    'get_loaded_assets',
    'unload',
    'unload_all',
    'set_max_load_time_per_frame',
    'Asset',
    'AssetConfig',
    'AssetSource',
    'Image',
    'ImageConfig',
    'Model',
    'ImageLoadData',
    'ModelLoadData')

# by default we allow to drop at most 1 frame while loading resources
_DEFAULT_MAX_LOAD_TIME_PER_FRAME = (1 / 60) * 1
_MAX_LOAD_THREADS = 4

AssetType = t.TypeVar('AssetType', bound=Asset)

@debug.profiled
def load_from_file(type: type[AssetType], filepath: str, config: AssetConfig) -> uuid.UUID:
    filepath = os.path.abspath(filepath)
    _check_file_exists(filepath)

    asset = _create_asset_object_from_filepath(type, filepath)
    _logger.debug('Created asset %s with id %s.', type.__name__, asset.id)

    _register_file_load_future(asset, config)
    _logger.info('Loading asset (type: %s, id: %s) from file "%s"...', type.__name__, asset.id, filepath)

    _insert_asset(asset)

    return asset.id

@debug.profiled
def load_from_data(type: type[AssetType], data: t.Any, config: AssetConfig) -> AssetType:
    asset = type(AssetSource.from_data(), uuid.uuid4())
    _logger.debug('Created asset %s with id %s.', type.__name__, asset.id)

    asset.load_from_data(data, config)
    asset.is_loaded = True
    _logger.info('Loaded asset (type: %s, id: %s) from data.', type.__name__, asset.id)

    _insert_asset(asset)

    return asset

@debug.profiled
def load_from_file_immediate(type: type[AssetType], filepath: str, config: AssetConfig) -> AssetType:
    filepath = os.path.abspath(filepath)
    _check_file_exists(filepath)

    asset = type(AssetSource.from_filepath(filepath), uuid.uuid4())
    _logger.debug('Created asset %s with id %s.', type.__name__, asset.id)

    _, load_data = asset.load_from_file(filepath, config)
    asset.post_load(load_data)

    _logger.info('Loaded asset (type: %s, id: %s) from file "%s".', type.__name__, asset.id, filepath)

    _insert_asset(asset)

    return asset

def add_asset(asset: Asset) -> uuid.UUID:
    _assets[asset.id] = asset

    return asset.id

@debug.profiled
def get(type: type[AssetType], id: uuid.UUID) -> AssetType:
    asset = _assets[id]
    assert isinstance(asset, type), 'Retrieved asset does not match requested type'

    return asset # type: ignore[return-value]

def get_or_empty(type: type[AssetType], id: uuid.UUID) -> AssetType:
    asset = get(type, id)
    if asset.is_loaded:
        return asset

    return get(type, type.get_empty_asset())

def get_loaded_assets() -> t.ValuesView[Asset]:
    return _assets.values()

@debug.profiled
def unload(id: uuid.UUID) -> None:
    if asset := _assets.pop(id, None):
        _unload(asset)

@debug.profiled
def unload_all() -> None:
    for asset in _assets.values():
        _unload(asset)

    _assets.clear()

@debug.profiled
def schedule_loading_tasks(scheduler: Scheduler, priority: int) -> None:
    while not _loading_queue.empty():
        load_future = _loading_queue.get_nowait()
        scheduler.schedule_main_thread_job(_process_loading_task, priority, load_future)

@debug.profiled
def process_loading_queue() -> None:
    load_start = time.perf_counter()

    while not _loading_queue.empty():
        load_future = _loading_queue.get_nowait()
        _process_loading_task(load_future)

        if time.perf_counter() - load_start > _max_load_time_per_frame:
            _logger.debug('Max asset loading time exceeded. Skipping loading rest of assets queue...')
            break

def set_max_load_time_per_frame(max_load_time_seconds: float) -> None:
    global _max_load_time_per_frame
    _max_load_time_per_frame = max_load_time_seconds

@debug.profiled
def _insert_asset(asset: Asset) -> None:
    _assets[asset.id] = asset

def _unload(asset: Asset) -> None:
    asset.unload()
    asset_unloaded_event.invoke(asset)

    _logger.info('Unloaded asset %s.', asset)

@debug.profiled
def _check_file_exists(filepath: str) -> None:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'Failed to find asset file "{filepath}".')

@debug.profiled
def _create_asset_object_from_filepath(asset_type: type[Asset], filepath: str) -> Asset:
    return asset_type(AssetSource.from_filepath(filepath), uuid.uuid4())

@debug.profiled
def _register_file_load_future(asset: Asset, config: AssetConfig) -> None:
    load_future = _asset_load_executor.submit(asset.load_from_file, asset.source.filepath, config)
    load_future.add_done_callback(lambda result: _loading_queue.put(result)) # type: ignore[arg-type]

@debug.profiled
def _process_loading_task(task: futures.Future[tuple[Asset, t.Any]]) -> None:
    if exc := task.exception():
        _logger.error('An error occured during asynchronous asset load: %s', exc)
    else:
        asset, load_data = task.result()

        _logger.debug('Finalizing asset load of %s (source: %s)...', type.__name__, asset.source)
        asset.post_load(load_data)

        asset_loaded_event.invoke(asset)

asset_loaded_event = events.Event[Asset]()
asset_unloaded_event = events.Event[Asset]()

_assets = dict[uuid.UUID, Asset]()
_logger = logging.getLogger(__name__)
_loading_queue = queue.Queue[futures.Future[tuple[Asset, t.Any]]]()
_max_load_time_per_frame = _DEFAULT_MAX_LOAD_TIME_PER_FRAME
_asset_load_executor = futures.ThreadPoolExecutor(_MAX_LOAD_THREADS, 'AssetLoad')
