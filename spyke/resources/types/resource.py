import abc
import threading
import uuid
import typing as t

class ResourceBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def get_suitable_extensions() -> t.List[str]:
        pass
    
    def __init__(self, _id: uuid.UUID, filepath: str):
        self.filepath = filepath
        self.id = _id
        self.is_internal = False
        self.is_loaded = False
        self._lock = threading.Lock()

    def __str__(self):
        return f'{type(self).__name__} from file {self.filepath}'

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
        if not self.is_loaded:
            return

        with self._lock:
            self._unload()

    @abc.abstractmethod
    def _unload(self) -> None:
        pass

# TODO: Add support for: Video?