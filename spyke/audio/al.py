from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
import logging
import ctypes as ct
from openal import al as AL
import openal


class ALObject(ABC):
    _objects: List[ALObject] = []

    @staticmethod
    def delete_all() -> None:
        cnt = len(ALObject._objects)

        for obj in ALObject._objects:
            obj._delete()

        ALObject._objects.clear()

        logging.log(logging.SP_INFO,
                    f'{cnt} OpenAL objects have been deleted.')

    @staticmethod
    def register(obj: ALObject) -> None:
        if obj in ALObject._objects:
            logging.log(logging.SP_INFO,
                        f'OpenAL object ({obj}) already registered.')
            return

        ALObject._objects.append(obj)

    @staticmethod
    def unregister(obj: ALObject) -> None:
        if obj not in ALObject._objects:
            return

        ALObject._objects.remove(obj)

    def __init__(self):
        self._id: openal.ALuint = openal.ALuint()
        self._deleted: bool = False

        ALObject.register(self)

    def __str__(self):
        return f'{type(self).__name__} (id: {self._id.value})'

    def __repr__(self):
        return str(self)

    def _delete(self) -> None:
        if self._deleted:
            return

        self.delete()
        ALObject.unregister(self)
        self._deleted = True

        logging.log(logging.SP_INFO, f'{self} deleted succesfully.')

    @abstractmethod
    def delete(self) -> None:
        pass

    @property
    def id(self) -> int:
        assert self._id != 0, f'Tried to use uninitialized OpenAL object ({self}).'
        assert not self._deleted, 'Tried to use OpenAL object that is already deleted.'

        return self._id


def generate_buffer() -> ct.c_uint:
    _id = ct.c_uint()
    AL.alGenBuffers(1, ct.pointer(_id))

    return _id


def delete_buffer(buffer: ct.c_uint) -> None:
    AL.alDeleteBuffers(1, ct.pointer(buffer))
