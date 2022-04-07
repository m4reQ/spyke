from __future__ import annotations
from uuid import UUID
from abc import ABC, abstractmethod
import threading

class Resource(ABC):
    def __init__(self, _id: UUID, filepath: str = ''):
        self._lock: threading.Lock = threading.Lock()
        self.filepath: str = filepath
        self.id: UUID = _id
        self.is_internal: bool = False
        self.is_invalid: bool = False

    def __str__(self):
        return f'{self.__class__.__name__} from file "{self.filepath}"'

    def __repr__(self):
        return str(self)
    
    @property
    def lock(self) -> threading.Lock:
        '''
        Returns thread lock that belongs to current resource,
        to prevent any errors that may happen while trying to render a
        resource that is still being loaded.
        '''

        return self._lock
    
    def unload(self) -> None:
        with self._lock:
            self._unload()
    
    @abstractmethod
    def _unload(self) -> None:
        pass

# TODO: Add support for: Video?
