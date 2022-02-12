from abc import ABC, abstractmethod
from typing import Any, TypeVar

LoadingData = TypeVar('LoadingData')


class Loader(ABC):
    __restypes__ = ''

    @abstractmethod
    def load(self, *args) -> LoadingData:
        pass

    @abstractmethod
    def finalize(self, loading_data: LoadingData, *args) -> Any:
        pass
