from .types import Event
from typing import TypeVar, Generic, Callable
import logging

T_Event = TypeVar('T_Event', bound=Event)
T_Return = TypeVar('T_Return')

_logger = logging.getLogger(__name__)

class Handler(Generic[T_Event, T_Return]):
    '''
    Represents a callable handler, which calls specific function
    to handle events of certain type.
    '''

    def __init__(self, function: Callable[[T_Event], T_Return], priority: int, consume: bool):
        self.func = function
        self.priority = priority
        self.consume = consume
    
    @property
    def name(self) -> str:
        return self.func.__qualname__

    def __call__(self, event: T_Event) -> T_Return:
        try:
            res = self.func(event)
        except Exception as e:
            _logger.error('An error occured in handler %s.', self.name, exc_info=e)

        if self.consume:
            event.consumed = True

        return res

    def __str__(self) -> str:
        return f'Handler from function: {self.func.__qualname__}'

    def __repr__(self) -> str:
        return str(self)
    
    def __hash__(self) -> int:
        return self.func.__hash__()