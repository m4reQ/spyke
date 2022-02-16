from __future__ import annotations
from spyke import debug
import typing

if typing.TYPE_CHECKING:
    from typing import Any
    from uuid import UUID

from spyke.exceptions import SpykeException
from spyke import loaders
from abc import ABC, abstractmethod
import time
from spyke import debug
from os import path


class Resource(ABC):
    @staticmethod
    def _get_resource_type(filepath: str) -> str:
        _, ext = path.splitext(filepath)
        return ext[1:].upper()

    def __init__(self, _id: UUID, filepath: str = ''):
        self.filepath: str = filepath
        self.is_internal: bool = False
        self.id: UUID = _id
        self._resource_type: str = Resource._get_resource_type(self.filepath)
        self._loader: loaders.Loader = loaders.get(self._resource_type)
        self._is_loaded: bool = False
        self._is_finalized: bool = False
        self._loading_data: Any = None
        self._loading_start: float = 0.0

    def __str__(self):
        return f'{self.__class__.__name__} from file "{self.filepath}"'

    def __repr__(self):
        return str(self)

    @abstractmethod
    def _load(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def _finalize(self) -> None:
        pass

    @abstractmethod
    def _unload(self) -> None:
        pass

    def unload(self) -> None:
        if not self.is_ready:
            logging.log(logging.SP_INFO,
                        f'Cannot unload not loaded resource ({self}).')
            return

        self._unload()
        self._is_loaded = False
        self._is_finalized = False

    def load(self, *args, **kwargs) -> None:
        if self.is_ready:
            logging.log(logging.SP_INFO,
                        f'Resource ({self}) is already loaded.')
            return

        self._loading_start = time.perf_counter()

        if __debug__:
            self._load(*args, **kwargs)
        else:
            try:
                self._load(*args, **kwargs)
            except Exception as e:
                raise SpykeException(
                    f'An exception occured while loading resource ({self}): {e}.') from e

        self._is_loaded = True

    def finalize(self) -> None:
        if not self._is_loaded:
            raise SpykeException(
                f'Cannot finalize loading of resource ({self}) that has not been fully loaded yet.')

        if self._is_finalized:
            logging.log(logging.SP_INFO,
                        f'Tried to finalize loading of resource ({self}) that already has been finalized.')

        if __debug__:
            self._finalize()
        else:
            try:
                self._finalize()
            except Exception as e:
                raise SpykeException(
                    f'An exception occured while finalizing resource ({self}) loading: {e}.') from e

        del self._loading_data
        del self._loader
        logging.log(logging.SP_INFO,
                    f'{self} loaded in {time.perf_counter() - self._loading_start} seconds.')
        self._is_finalized = True

    @property
    def is_ready(self) -> bool:
        return self._is_loaded and self._is_finalized

# TODO: Add support for: Model, Sound, Video?
