from __future__ import annotations
from typing import Generic, TypeVar, Callable, Type, Dict, List, Any
import inspect
import sys
import queue
import threading
import logging
from spyke.exceptions import SpykeException
from . import types
from .types import *

__all__ = [
    'Event',
    'KeyDownEvent',
    'KeyUpEvent',
    'ResizeEvent',
    'MouseButtonDownEvent',
    'MouseButtonUpEvent',
    'MouseMoveEvent',
    'MouseScrollEvent',
    'WindowMoveEvent',
    'WindowChangeFocusEvent',
    'WindowCloseEvent',
    'ToggleVsyncEvent',
    'ResourceLoadedEvent',
    'Handler',
    'register_user_event',
    'invoke',
    'register',
]

T_Event = TypeVar('T_Event', bound=Event)
T_Return = TypeVar('T_Return')

_handlers: Dict[Type[Event], List[Handler]] = dict()
_events: queue.Queue[Event] = queue.Queue(maxsize=128)

_LOGGER = logging.getLogger(__name__)

class Handler(Generic[T_Event, T_Return]):
    '''
    Represents a callable handler, which calls specific function
    to handle events of certain type.
    '''

    def __init__(self, function: Callable[[T_Event], T_Return], priority: int, consume: bool):
        self.func = function
        self.priority = priority
        self.consume = consume

    def __call__(self, event: T_Event) -> T_Return:
        try:
            res = self.func(event)
        except Exception as e:
            raise SpykeException(f'An error occured in handler "{self.func.__name__}": {e}.') from None

        if self.consume:
            event.consumed = True

        return res

    def __str__(self) -> str:
        return f'Handler from function: {self.func.__qualname__}'

    def __repr__(self) -> str:
        return str(self)
    
    def __hash__(self) -> int:
        return self.func.__hash__()

def register(method: Callable[[T_Event], Any], event_type: Type[T_Event], *, priority: int, consume: bool = False) -> None:
    '''
    Registers method as a handler for events of given type.

    @method: Method that will be used as an event handler.
    @event_type: Type of events will trigger registered function.
    @priority: The priority tells event system in what order to call registered functions.
    @consume: Indicates if handler should consume the event and stop further calls to other handlers.

    Raises:
        - (DEBUG) `AssertionError` if user tries to register function with negative
        priority, that is not a part of spyke engine.
    '''

    assert not (priority < 0 and not method.__module__.startswith('spyke')), 'Negative priority is reserved for internal engine handlers and cannot be used to register user-defined functions.'

    handler = Handler(method, priority, consume)
    
    if event_type not in _handlers:
        raise SpykeException(f'Unknown event type: {event_type.__name__}. Maybe you forgot to register it using "register_user_event".')

    if handler in _handlers[event_type]:
        _LOGGER.warning('Handler %s already registered for event type: %s.', handler, event_type.__name__)
        return
    
    _handlers[event_type].append(handler)
    _handlers[event_type].sort(key=lambda x: x.priority)

    _LOGGER.debug('Function %s registered for %s (priority: %d, consume: %s).', method.__qualname__, event_type.__name__, priority, consume)

def invoke(event: Event) -> None:
    '''
    Put an event into event queue.
    Any handlers will not be actually invoked until
    the `events._process_events` function is called.
    This function does not block the caller thread and will not
    raise an error even if the event queue is full (it will get logged though).

    @event: Object that represents an event. Must be subclass of Event.

    Raises:
        - (DEBUG) `AssertionError` if event type was not previously registered with `events.register_user_event`.
    '''

    assert type(event) in _handlers, f'Unknown event type: {type(event).__name__}. Maybe you forgot to register it using "register_user_event".'

    try:
        _events.put_nowait(event)
        _LOGGER.debug('Event invocation for %s', event)
    except queue.Full:
        _LOGGER.warning('Cannot enqueue event of type %s. Event queue full.', type(event).__name__)

def _init() -> None:
    _types = inspect.getmembers(sys.modules[types.__name__], inspect.isclass)
    for _, _type in _types:
        if _type != Event and issubclass(_type, Event):
            _handlers[_type] = list()
    
    _LOGGER.debug('Events module initialized.')

def _process_events() -> None:
    '''
    Processes events that are present in event queue
    by calling appropriate handlers.

    The function should not be called by user code, howewer it
    does not have any guard that will check for such circumstance.
    Additionally `events._process_events` has to be called from main
    thread. Otherwise it will raise an exception (this does not apply
    when running with optimization enabled).

    Be aware that this function can process only certain
    amount of events per call. This amount is controlled by a constant
    `MAX_EVENTS_PROCESSED`.

    Raises:
        - (DEBUG) `AssertionError` if the caller thread is not main thread.
    '''

    assert threading.current_thread() is threading.main_thread(), 'events._process_events has to be called from main thread.'

    while True:
        try:
            event = _events.get_nowait()
        except queue.Empty:
            return

        for handler in _handlers[type(event)]:
            if event.consumed:
                break
            
            handler(event)

def register_user_event(event_type: Type[Event]) -> None:
    '''
    Registers new user-defined event type. User-defined event types
    have to be subclasses of Event class.

    @event_type: Type of event that will be registered.

    Raises:
        - `RuntimeError` if event type passed to function does not inherit from `Event` class.
    '''

    if not issubclass(event_type, Event):
        raise RuntimeError('User-defined events have to be subclasses of the Event class.')

    if event_type in _handlers:
        _LOGGER.warning('User-defined event type %s already registered.', event_type.__name__)
        return

    _handlers[event_type] = list()

    _LOGGER.debug('Registered new user event %s', event_type.__name__)