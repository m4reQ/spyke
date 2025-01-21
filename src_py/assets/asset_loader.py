import abc
import typing as t

from spyke.assets.asset_config import AssetConfig


class AssetLoader(abc.ABC):
    @abc.abstractmethod
    def can_process_file_data(self, file_data: bytes) -> bool:
        pass

    @abc.abstractmethod
    def load_from_binary(self, data: bytes, config: AssetConfig) -> t.Any:
        pass
