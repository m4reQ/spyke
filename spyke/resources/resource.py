from __future__ import annotations
from spyke import debug
from uuid import UUID
from abc import ABC, abstractmethod

class Resource(ABC):
    def __init__(self, _id: UUID, filepath: str = ''):
        self.filepath: str = filepath
        self.id: UUID = _id
        self.is_internal: bool = False
        self.is_invalid: bool = False

    def __str__(self):
        return f'{self.__class__.__name__} from file "{self.filepath}"'

    def __repr__(self):
        return str(self)
    
    def unload(self) -> None:
        self._unload()
        debug.log_info(f'Resource ({self}) unloaded.')
    
    @classmethod
    def invalid(cls, _id: UUID):
        '''
        Returns resource that is marked invalid and will not be used.
        '''

        resource = cls(_id)
        resource.is_invalid = True

        return resource

    @abstractmethod
    def _unload(self) -> None:
        pass

# TODO: Add support for: Model, Video?
