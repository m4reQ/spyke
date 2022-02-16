from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from spyke import debug
import atexit


class Deletable(ABC):
    '''
    Represents an object that should call additional code
    before it is deleted.
    '''

    _objects: List[Deletable] = []

    @staticmethod
    def _register(obj: Deletable) -> None:
        if obj in Deletable._objects:
            return

        Deletable._objects.append(obj)
        debug.log_info(f'Deletable object of type {type(obj).__name__} registered.')

    @staticmethod
    def _unregister(obj: Deletable) -> None:
        if obj not in Deletable._objects:
            return

        Deletable._objects.remove(obj)
        debug.log_info(f'Deletable object of type {type(obj).__name__} unregistered.')

    @staticmethod
    def delete_all() -> None:
        cnt = len(Deletable._objects)

        for obj in reversed(Deletable._objects):
            obj._delete()

        Deletable._objects.clear()

        debug.log_info(f'{cnt} deletable objects have been deleted.')

    def __init__(self):
        self._deleted: bool = False
        Deletable._register(self)

    @abstractmethod
    def _delete(self) -> None:
        pass

    def delete(self) -> None:
        if self._deleted:
            return

        self._delete()
        Deletable._unregister(self)
        self._deleted = True

        debug.log_info(f'{self} deleted succesfully.')

atexit.register(Deletable.delete_all)