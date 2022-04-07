from __future__ import annotations
from spyke.resources.types.resource import Resource
from spyke import events
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Type
import logging
import threading
import time

class LoadingData(ABC):
    pass

T_Resource = TypeVar('T_Resource', bound=Resource)
T_LoadingData = TypeVar('T_LoadingData', bound=LoadingData)

_LOGGER = logging.getLogger(__name__)

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

    def __init__(self, resource: T_Resource):
        self._thread: threading.Thread = threading.Thread(target=self._target)
        self._loading_start: float = 0.0
        self._had_loading_error: bool = False
        self._data: T_LoadingData
        self.resource: T_Resource = resource
    
    @abstractmethod
    def _load(self) -> None:
        '''
        Loads data from file with path passed to constructor.
        '''

        pass
    
    @abstractmethod
    def finalize(self) -> None:
        '''
        Creates handles that are required to be initialized in main
        thread (such as OpenGL textures) and places them in current resource.
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

        try:
            self._load()
        except Exception as e:
            self._had_loading_error = True
            _LOGGER.error('An error happened during resource (%s) loading: %s.', self.filepath, e)
        else:
            _LOGGER.info('Resource from file "%s" loaded in %f seconds.', self.filepath, time.perf_counter() - self._loading_start)

        # NOTE: There is a possibility that we are not able to invoke any more events
        # as our queue is becomes full. This leads to a resource that cannot be loaded anymore.
        events.invoke(events.ResourceLoadedEvent(self))

    def start(self) -> None:
        '''
        Starts Loader's loading thread.
        '''

        self._loading_start = time.perf_counter()
        self._thread.start()

        _LOGGER.debug('Started loading resource from file "%s".', self.filepath)
    
    @property
    def filepath(self) -> str:
        return self.resource.filepath
    
    @property
    def had_loading_error(self) -> bool:
        return self._had_loading_error