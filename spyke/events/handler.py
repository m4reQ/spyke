from .types import Event
from typing import TypeVar, Generic, Callable
import logging

_ET = TypeVar('_ET', bound=Event)
_RT = TypeVar('_RT')

_logger = logging.getLogger(__name__)

class Handler(Generic[_ET, _RT]):
    '''
    Represents a callable handler, which calls specific function
    to handle events of certain type.
    '''

    def __init__(self, function: Callable[[_ET], _RT], priority: int, consume: bool):
        self.func = function
        self.priority = priority
        self.consume = consume
    
    @property
    def name(self) -> str:
        return self.func.__qualname__

    def __call__(self, event: _ET) -> _RT:
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