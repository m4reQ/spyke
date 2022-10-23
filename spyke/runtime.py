import abc
import atexit
import logging
import queue
import time
import typing as t
from concurrent import futures

from spyke.utils import once

MAX_PROCESS_WAIT_TIME = 0.16
EXECUTOR = futures.ThreadPoolExecutor(thread_name_prefix='spyke_bg_thread')

_ReturnType = t.TypeVar('_ReturnType')
_Params = t.ParamSpec('_Params')

class DisposableBase(abc.ABC):
    '''
    Represents an object that should call additional code
    before it gets deleted.
    '''

    def __init__(self) -> None:
        _register_object(self)
        self._is_disposed = False

    @property
    def is_disposed(self) -> bool:
        return self._is_disposed

    @abc.abstractmethod
    def _dispose(self) -> None:
        pass

    def dispose(self) -> None:
        if self._is_disposed:
            raise RuntimeError('Object has been already deleted.')

        self._dispose()

@once
def initialize() -> None:
    atexit.register(_dispose_all)

    for func in _startup:
        func()

def process_pending_futures() -> None:
    current_time = 0.0
    while True:
        start = time.perf_counter()
        if current_time > MAX_PROCESS_WAIT_TIME:
            return

        if _callbacks.empty():
            break

        cb, result = _callbacks.get_nowait()
        cb(result)

        current_time += time.perf_counter() - start

def submit_future(func: t.Callable[_Params, _ReturnType],
           *args: _Params.args, # type: ignore
           callback: t.Callable[[_ReturnType], t.Any] | None = None,
           **kwargs: _Params.kwargs) -> futures.Future[_ReturnType]: # type: ignore
    future = _executor.submit(func, *args, **kwargs)
    if callback is not None:
        future.add_done_callback(lambda x: _callbacks.put_nowait((callback, x.result()))) # type: ignore

    return future

def register_startup_function(function: t.Callable[_Params, t.Any], *args: _Params.args, **kwargs: _Params.kwargs) -> None:
    '''
    Registers function that has to be executed when this module is initialized

    @func: A callable to be registered.
    @*args: Arguments that will be passed to the function.
    @**kwargs: Keyword arguments that will be passed to the function.
    '''

    _startup.append(lambda: function(*args, **kwargs))

def register_dispose_function(function: t.Callable[_Params, t.Any], *args: _Params.args, **kwargs: _Params.kwargs) -> None:
    '''
    Registers functions that has to be executed when the program finishes.
    Calls to all registered functions are made using `atexit` module.

    @func: A callable to be registered.
    @*args: Arguments that will be passed to the function.
    @**kwargs: Keyword arguments that will be passed to the function.
    '''

    _tear_down.append(lambda: function(*args, **kwargs))

def _register_object(obj: DisposableBase) -> None:
    _objects.append(obj)

def _dispose_all() -> None:
    for obj in reversed(_objects):
        obj.dispose()

        _logger.info('Object %s has been succesfully deleted.', obj)

    _objects.clear()

    for func in reversed(_tear_down):
        try:
            func()
        except Exception as e:
            _logger.error(f'An error occured while executing dispose callback %s', func.__qualname__, exc_info=e)

        _logger.info('Dispose function %s has been called.', func.__qualname__)

    _tear_down.clear()

_objects: list[DisposableBase] = []
_tear_down: list[t.Callable[[], t.Any]] = []
_logger = logging.getLogger(__name__)
_executor = futures.ThreadPoolExecutor(thread_name_prefix='spyke_bg_thread')
_callbacks = queue.Queue[tuple[t.Callable[..., t.Any], t.Any]]()
_startup: list[t.Callable[[], t.Any]] = []
