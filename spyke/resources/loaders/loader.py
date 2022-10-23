import abc
import typing as t

from spyke.resources.types.resource import ResourceBase

_Resource = t.TypeVar('_Resource', bound=ResourceBase)
_LoadingData = t.TypeVar('_LoadingData')

class LoaderBase(abc.ABC, t.Generic[_Resource, _LoadingData]):
    __supported_extensions__: list[str] = []

    @staticmethod
    @abc.abstractmethod
    def load_from_file(filepath: str) -> _LoadingData: ...

    @staticmethod
    @abc.abstractmethod
    def finalize_loading(resource: _Resource, loading_data: _LoadingData) -> None: ...
