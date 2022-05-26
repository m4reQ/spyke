import abc
import typing as t
import threading
import time
from spyke.resources import loading_queue

from spyke.resources.types.resource import ResourceBase

T_Resource = t.TypeVar('T_Resource', bound=ResourceBase)
class LoaderBase(threading.Thread, abc.ABC, t.Generic[T_Resource]):
    def __init__(self, resource: T_Resource):
        super().__init__(target=self._load, args=(resource.filepath,))

        self.resource = resource
        self.loading_data: t.Any = None
        self.loading_error: t.Optional[Exception] = None

        self._loading_start = 0.0

    @abc.abstractmethod
    def load(self, filepath: str) -> t.Any:
        pass

    @abc.abstractmethod
    def finish_loading(self) -> None:
        pass

    @property
    def has_loading_error(self) -> bool:
        return self.loading_error is not None

    @property
    def loading_time(self) -> float:
        return time.perf_counter() - self._loading_start

    def _load(self, filepath: str) -> None:
        self._loading_start = time.perf_counter()
        try:
            self.loading_data = self.load(filepath)
        except Exception as e:
            self.loading_error = e

        loading_queue.put_loader(self)
