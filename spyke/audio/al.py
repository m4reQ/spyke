from __future__ import annotations
from abc import ABC
from spyke.utils import Deletable
import ctypes as ct
from openal import al as AL
import openal


class ALObject(Deletable, ABC):
    def __init__(self):
        super().__init__()
        self._id: openal.ALuint = openal.ALuint(0)

    def __str__(self):
        return f'{type(self).__name__} (id: {self._id.value})'

    def __repr__(self):
        return str(self)

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
