from abc import ABC, abstractmethod
from typing import Any, TypeVar, Union, List

LoadingData = TypeVar('LoadingData')


class Loader(ABC):
    __restypes__: Union[List[str], str] = ''

    @abstractmethod
    def load(self, *_) -> LoadingData:
        pass

    @abstractmethod
    def finalize(self, loading_data: LoadingData, *args) -> Any:
        pass
