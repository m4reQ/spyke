import logging
import os
import queue
import time
import typing as t
import uuid
from concurrent import futures

from spyke import debug, events
from spyke.assets.asset import Asset, AssetConfig, AssetSource

# by default we allow to drop at most 1 frame while loading resources
_DEFAULT_MAX_LOAD_TIME_PER_FRAME = (1 / 60) * 1
_MAX_LOAD_THREADS = 4

AssetType = t.TypeVar('AssetType', bound=Asset)

@debug.profiled('assets')
def load_from_file(type: type[AssetType], filepath: str, config: AssetConfig) -> uuid.UUID:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'Failed to find asset file "{filepath}".')

    asset_id = uuid.uuid4()

    asset_source = AssetSource.from_filepath(filepath)
    asset = type(asset_source, asset_id)

    load_future = _asset_load_executor.submit(asset.load_from_file, filepath, config)
    load_future.add_done_callback(lambda result: _loading_queue.put(result)) # type: ignore[arg-type]

    _assets[asset_id] = asset

    return asset_id

@debug.profiled('assets')
def load_from_data(type: type[AssetType], data: t.Any, config: AssetConfig) -> uuid.UUID:
    asset_id = uuid.uuid4()

    asset_source = AssetSource.from_data()
    asset = type(asset_source, asset_id)

    asset.load_from_data(data, config)
    asset.is_loaded = True

    _assets[asset_id] = asset

    return asset_id

def add_asset(asset: Asset) -> uuid.UUID:
    _assets[asset.id] = asset

    return asset.id

@debug.profiled('assets')
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

@debug.profiled('assets')
def unload(id: uuid.UUID) -> None:
    if asset := _assets.pop(id, None):
        _unload(asset)

@debug.profiled('assets')
def unload_all() -> None:
    for asset in _assets.values():
        _unload(asset)

    _assets.clear()

@debug.profiled('assets')
def process_loading_queue() -> None:
    load_start = time.perf_counter()

    while not _loading_queue.empty():
        load_future = _loading_queue.get_nowait()
        if exc := load_future.exception():
            raise RuntimeError('An error occured during asset load.') from exc

        asset, load_data = load_future.result()
        asset.post_load(load_data)

        asset_loaded_event.invoke(asset)

        if time.perf_counter() - load_start > _max_load_time_per_frame:
            _logger.debug('Max asset loading time exceeded. Skipping loading rest of assets queue...')
            break

def set_max_load_time_per_frame(max_load_time_seconds: float) -> None:
    global _max_load_time_per_frame
    _max_load_time_per_frame = max_load_time_seconds

def _unload(asset: Asset) -> None:
    asset.unload()
    asset_unloaded_event.invoke(asset)

    _logger.info('Unloaded asset %s.', asset)

asset_loaded_event = events.Event[Asset]()
asset_unloaded_event = events.Event[Asset]()

_assets = dict[uuid.UUID, Asset]()
_logger = logging.getLogger(__name__)
_loading_queue = queue.Queue[futures.Future[tuple[Asset, t.Any]]]()
_max_load_time_per_frame = _DEFAULT_MAX_LOAD_TIME_PER_FRAME
_asset_load_executor = futures.ThreadPoolExecutor(_MAX_LOAD_THREADS, 'AssetLoad')
