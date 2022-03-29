from __future__ import annotations
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic, List, Type
# TODO: Import TypeGuard from typing when we move to Python 3.10
from typing_extensions import TypeGuard
from uuid import UUID
from ..resource import Resource
from spyke import debug

class LoadingData(ABC):
    pass

T_Resource = TypeVar('T_Resource', bound=Resource)
T_LoadingData = TypeVar('T_LoadingData', bound=LoadingData)

class Loader(Generic[T_LoadingData, T_Resource], ABC):
    '''
    Represents resource loader that handles data load and handles and
    resources creation.
    Every subclass of `Loader` has to contain those two class variables:
    - `__extensions__` which is a list of file extension names for which loader will be registered
    - `__restype__` which is a type of resource that will be created by `Loader.finalize` method
    '''

    # TODO: Make static typing on these variables work
    __extensions__: List[str] = list()
    __restype__: Type[T_Resource]

    def __init__(self, _id: UUID, filepath: str):
        self._thread: threading.Thread = threading.Thread(target=self._target)
        self._data: Optional[T_LoadingData] = None
        self._finish_flag: threading.Event = threading.Event()
        self._loading_start: float = 0.0
        self.filepath: str = filepath
        self.id: UUID = _id
    
    @abstractmethod
    def _load(self) -> None:
        '''
        Loads data from file with path passed to constructor.
        '''

        pass
    
    @abstractmethod
    def finalize(self) -> T_Resource:
        '''
        Creates handles that are required to be initialized in main
        thread (such as OpenGL textures).
        By default this function only makes sure that loaded data is actually
        present.

        Raises:
            - (DEBUG) `AssertionError` if `Loader._data` is None.
        '''

        pass

    def _target(self) -> None:
        '''
        Loader's thread target.
        '''

        self._load()
        self._finish_flag.set()
        debug.log_info(f'Resource from file "{self.filepath}" loaded in {time.perf_counter() - self._loading_start} seconds.')

    def start(self) -> None:
        '''
        Starts Loader's loading thread.
        '''

        self._loading_start = time.perf_counter()
        self._thread.start()
    
    def wait(self) -> None:
        '''
        Wait for loader to finish its work.
        '''

        self._finish_flag.wait()
    
    def _check_data_valid(self, data: Optional[T_LoadingData]) -> TypeGuard[T_LoadingData]:
        '''
        Checks if data was loaded succesfully.
        '''

        assert data is not None, 'Loader._load has been called, but data is None.'
        return True