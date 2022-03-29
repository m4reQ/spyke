from __future__ import annotations
from spyke.utils import Deletable
from abc import ABC
from openal import ALuint


class ALObject(Deletable, ABC):
    def __init__(self):
        super().__init__()

        self._id: ALuint = ALuint()

    def __str__(self):
        return f'{type(self).__name__} (id: {self._id.value}) {"(deleted)" if self._deleted else ""}'

    def __repr__(self):
        return str(self)

    @property
    def id(self) -> int:
        assert self._id.value != 0, f'Tried to use uninitialized OpenAL object ({self}).'
        assert not self._deleted, 'Tried to use OpenAL object that is already deleted.'

        return self._id.value