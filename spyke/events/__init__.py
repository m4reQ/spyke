from spyke import debug
from spyke.exceptions import SpykeException
from . import types
from .types import *
from typing import TypeVar, Callable
import inspect
import sys

EventType = TypeVar('EventType', bound=types.Event)
ReturnType = TypeVar('ReturnType')

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
    'Handler',
    'register_user_event',
    'invoke',
    'register',
    'register_method'
]

_handlers = {}

# get all internal event types and create
# stores for their handlers
_types = inspect.getmembers(sys.modules[types.__name__], inspect.isclass)
for _, _type in _types:
    if _type != types.Event and issubclass(_type, types.Event):
        _handlers[_type] = list()


class Handler:
    '''
    Represents a usable handler, which calls specific function
    to handle events of certain type.
    '''

    def __init__(self, function: Callable[[EventType], ReturnType], priority: int, consume: bool):
        self.func = function
        self.priority = priority
        self.consume = consume

    def __call__(self, event: EventType) -> ReturnType:
        try:
            res = self.func(event)
        except Exception as e:
            raise SpykeException(
                f'An error occured in handler "{self.func.__name__}": {e}.') from None

        if self.consume:
            event.consumed = True

        return res


def register_method(method: Callable[[EventType], ReturnType], event_type: EventType, *, priority: int, consume: bool = False) -> None:
    '''
    Registers method bound to an object as a handler for events of given type.

    :param method: Method that will be used as an event handler.

    :param event_type: Indicates what type of events will trigger
    registered function.

    :param priority: The priority tells event system in what order
    to call registered functions. -1 is reserved for internal handlers
    and will throw an error when user tries to use it.

    :param consume: Indicates if handler should consume the event and
    stop further calls to other handlers.
    '''

    handler = Handler(method, priority, consume)

    if handler in _handlers:
        debug.log_warning(
            f'Handler {handler.__name__} already registered for event type: {event_type.__name__}.')
        return

    # raise error when we try to register funciton thats not part
    # of spyke module, with negative priority
    if priority < 0 and not method.__module__.startswith('spyke'):
        raise SpykeException(
            'Negative priority is reserved for internal engine handlers and cannot be used to register user-defined functions.')

    _handlers[event_type].append(handler)
    _handlers[event_type].sort(key=lambda x: x.priority)

    debug.log_info(
        f'Function {method.__name__} registered for {event_type.__name__} (priority: {priority}, consume: {consume}).')


# TODO: Make register funciton accept bound methods
def register(event_type: EventType, *, priority: int, consume: bool = False) -> Callable[[EventType], ReturnType]:
    '''
    Registers new function as a handler for events of given type. Should be used as a decorator.
    Warning: this function cannot register bound methods as event handlers. To do this use "register_method" function.

    :param event_type: Indicates what type of events will be triggering
    registered function.

    :param priority: The priority tells event system in what order
    to call registered functions. -1 is reserved for internal handlers
    and will throw an error when user tries to use it.

    :param consume: Indicates if handler should consume the event and
    stop further calls to other handlers.
    '''

    def inner(handler_fn: Callable[[EventType], ReturnType]):
        # check if we are dealing with bound method
        if '.' in handler_fn.__qualname__:
            raise SpykeException(
                'Cannot register bound method as event handler using "register". Please use "register_method" instead.')

        handler = Handler(handler_fn, priority, consume)

        def wrapper(event: EventType):
            return handler(event)

        if handler in _handlers:
            debug.log_warning(
                f'Handler {handler.__name__} already registered for event type: {event_type.__name__}.')
            return wrapper

        # raise error when we try to register funciton thats not part
        # of spyke module, with negative priority
        if priority < 0 and not handler_fn.__module__.startswith('spyke'):
            raise SpykeException(
                'Negative priority is reserved for internal engine handlers and cannot be used to register user-defined functions.')

        _handlers[event_type].append(handler)
        _handlers[event_type].sort(key=lambda x: x.priority)

        debug.log_info(
            f'Function {handler_fn.__name__} registered for {event_type.__name__} (priority: {priority}, consume: {consume}).')

        return wrapper

    return inner


def invoke(event: types.Event) -> None:
    '''
    Invokes all handlers registered for given event type
    with the event object.

    :param event: Object that represents an event. Must be subclass of Event.
    '''

    event_type = type(event)

    if not event_type in _handlers:
        raise RuntimeError(
            f'Invalid event type: {event_type}. Maybe you forgot to register it using "register_user_event".')

    for handler in _handlers[event_type]:
        if event.consumed:
            break

        handler(event)


def register_user_event(event_type: types.Event) -> None:
    '''
    Registers new user-defined event type. User-defined event types
    have to be subclasses of Event class.

    :param event_type: Type of event that will be registered.
    '''

    if not issubclass(event_type, types.Event):
        raise RuntimeError(
            'User-defined events have to be subclasses of the Event class.')

    if event_type in _handlers:
        debug.log_warning(
            f'User-defined event type "{event_type.__name__}" already registered.')
        return

    _handlers[event_type] = list()