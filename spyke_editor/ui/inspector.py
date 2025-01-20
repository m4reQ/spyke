import abc
import typing as t

ItemType = t.TypeVar('ItemType')

class Inspector(abc.ABC, t.Generic[ItemType]):
    @abc.abstractmethod
    def get_supported_types(self) -> tuple[type]:
        pass

    @abc.abstractmethod
    def render(self, item: ItemType) -> None:
        pass
