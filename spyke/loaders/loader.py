from abc import ABC, abstractmethod
from typing import Any


class Loader(ABC):
    __restypes__ = ''

    @abstractmethod
    def load(self, *args) -> Any:
        pass

    @abstractmethod
    def finalize(self, *args) -> Any:
        pass
