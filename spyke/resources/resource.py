from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Any
    from uuid import UUID

from spyke.exceptions import SpykeException
from abc import ABC, abstractmethod
import time
from spyke import debug


class Resource(ABC):
    def __init__(self, _id: UUID, filepath: Optional[str] = None):
        self.filepath: Optional[str] = filepath
        self.is_internal: bool = False
        self.id: UUID = id
        self._is_loaded: bool = False
        self._is_finalized: bool = False
        self._loading_data: Dict[str, Any] = {}
        self._loading_start: float = 0.0

    def __str__(self):
        return f'{self.__class__.__name__} from file "{self.filepath}"'

    def __repr__(self):
        return str(self)

    @abstractmethod
    def _load(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def _unload(self) -> None:
        pass

    @abstractmethod
    def _finalize(self) -> None:
        pass

    @abstractmethod
    def _unload(self) -> None:
        pass

    def unload(self) -> None:
        if not self.is_ready:
            debug.log_warning(f'Cannot unload not loaded resource ({self}).')
            return

        self._unload()
        self._is_loaded = False
        self._is_finalized = False

    def load(self, *args, **kwargs) -> None:
        if self.is_ready:
            debug.log_warning(f'Resource ({self}) is already loaded.')
            return

        self._loading_start = time.perf_counter()

        try:
            self._load(*args, **kwargs)
        except Exception as e:
            raise SpykeException(
                f'An exception occured while loading resource ({self}): {e}.') from None

        self._is_loaded = True

    def finalize(self) -> None:
        if not self._is_loaded:
            raise SpykeException(
                f'Cannot finalize loading of resource ({self}) that has not been fully loaded yet.')

        if self._is_finalized:
            debug.log_warning(
                f'Tried to finalize loading of resource ({self}) that already has been finalized.')

        try:
            self._finalize()
        except Exception as e:
            raise SpykeException(
                f'An exception occured while finalizing resource ({self}) loading: {e}.') from None

        self._is_finalized = True

    def cleanup(self) -> None:
        '''
        Removes unnecessary loading data after resource loading is finalized.
        '''

        if not self.is_ready:
            debug.log_warning(
                f'Tried to clean up resource ({self}) that is not loaded yet.')
            return

        self._loading_data.clear()

    @property
    def is_ready(self) -> bool:
        return self._is_loaded and self._is_finalized

# TODO: Add support for: Model, Sound, Video?
