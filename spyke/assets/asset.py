import dataclasses
import logging
import threading
import typing as t
import uuid

from spyke.assets.asset_config import AssetConfig
from spyke.assets.asset_loader import AssetLoader
from spyke.assets.asset_source import AssetSource


@dataclasses.dataclass(eq=False)
class Asset:
    source: AssetSource
    id: uuid.UUID = dataclasses.field(repr=False)
    is_loaded: bool = dataclasses.field(repr=False, default=False)

    _loading_lock: threading.Lock = dataclasses.field(repr=False, default_factory=threading.Lock)

    __associated_loaders: t.ClassVar[set[AssetLoader]] = set()
    __empty_asset: t.ClassVar[t.Self | None] = None

    @classmethod
    def register_loader(cls, loader: AssetLoader) -> None:
        cls.__associated_loaders.add(loader)
        _logger.debug('Registered loader %s for asset of type %s.', type(loader).__name__, cls.__name__)

    @classmethod
    def get_empty_asset(cls) -> uuid.UUID:
        assert cls.__empty_asset is not None, 'Empty asset not initialized'
        return cls.__empty_asset.id

    @classmethod
    def register_empty_asset(cls, asset: t.Self) -> None:
        cls.__empty_asset = asset

    # TODO Fix typing on Asset.load_from_file
    def load_from_file(self, filepath: str, config: AssetConfig) -> tuple[t.Self, t.Any]:
        with open(filepath, 'rb') as f:
            file_data = f.read()

        loader = self._find_suitable_loader(file_data)
        loading_data = loader.load_from_binary(file_data, config)

        return (self, loading_data)

    def load_from_data(self, data: t.Any, config: AssetConfig) -> None:
        pass

    def post_load(self, load_data: t.Any) -> None:
        pass

    def unload(self) -> None:
        pass

    def _find_suitable_loader(self, file_data: bytes) -> AssetLoader:
        for loader in self.__associated_loaders:
            if loader.can_process_file_data(file_data):
                return loader

        raise RuntimeError(f'Failed to find suitable loader that could load asset {type(self).__name__} from file data.')

_logger = logging.getLogger(__name__)
