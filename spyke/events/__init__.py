import typing as t
import inspect
import queue
import threading
import logging

from spyke import debug
from spyke.utils import class_registrant
from . import types
from .types import *
from .handler import Handler

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

_ET = t.TypeVar('_ET', bound=Event)

_handlers: dict[type[Event], list[Handler]] = {}
_events: queue.Queue[Event] = queue.Queue(maxsize=128)

_logger = logging.getLogger(__name__)

def register(method: t.Callable[[_ET], t.Any], event_type: type[_ET], *, priority: int, consume: bool = False) -> None:
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

    if priority < 0 and not _is_function_from_engine(method):
        _logger.error('Negative priority is reserved for internal engine handlers and cannot be used to register user-defined functions.')
        return

    handler = Handler(method, priority, consume)
    event_name = event_type.__name__
    
    if event_type not in _handlers:
        _logger.error('Unknown event type: %s. Maybe you forgot to register it using "register_user_event".', event_name)
        return

    if handler in _handlers[event_type]:
        _logger.warning('Handler %s already registered for event type: %s.', handler, event_name)
        return
    
    _handlers[event_type].append(handler)
    _handlers[event_type].sort(key=lambda x: x.priority)

    _logger.debug('Function %s registered for %s (priority: %d, consume: %s).', method.__qualname__, event_name, priority, consume)

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
        _logger.debug('Event invocation for %s', event)
    except queue.Full:
        _logger.warning('Cannot enqueue event of type %s. Event queue full.', type(event).__name__)

@debug.profiled('events')
def process_events() -> None:
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

    while not _events.empty():
        event = _events.get_nowait()
        
        for handler in _handlers[type(event)]:
            if event.consumed:
                break
            
            handler(event)

def register_user_event(event_type: type[Event]) -> None:
    '''
    Registers new user-defined event type. User-defined event types
    have to be subclasses of Event class.

    @event_type: Type of event that will be registered.

    Raises:
        - `RuntimeError` if event type passed to function does not inherit from `Event` class.
    '''

    if not issubclass(event_type, Event):
        _logger.error('User-defined events have to be subclasses of the Event class.')
        return

    if event_type in _handlers:
        _logger.warning('User-defined event type %s already registered.', event_type.__name__)
        return

    _handlers[event_type] = list()

    _logger.debug('Registered new user event %s', event_type.__name__)

def _register_events() -> None:
    classes = inspect.getmembers(types, predicate=lambda x: inspect.isclass(x) and not inspect.isabstract(x) and issubclass(x, Event))
    for name, _class in classes:
        if _class in _handlers:
            _logger.warning('Event %s already registered.', name)
        
        _handlers[_class] = []
        _logger.debug('Event %s registered succesfully.', name)

def _is_function_from_engine(func: t.Callable) -> bool:
    return func.__module__.startswith('spyke')

_register_events()
_logger.debug('Events module initialized.')