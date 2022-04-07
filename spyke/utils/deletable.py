from __future__ import annotations
from abc import ABC, abstractmethod
import logging

_LOGGER = logging.getLogger(__name__)

class Deletable(ABC):
    '''
    Represents an object that should call additional code
    before it is deleted.
    '''

    def __init__(self):
        self._deleted: bool = False

    @abstractmethod
    def _delete(self) -> None:
        pass

    def delete(self) -> None:
        if self._deleted:
            return

        self._delete()
        self._deleted = True

        _LOGGER.debug('%s deleted succesfully.', self)