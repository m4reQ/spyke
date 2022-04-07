from __future__ import annotations
from typing import Optional
from spyke.enums import SoundFormat
from spyke.audio import ALObject
from openal import al
import numpy as np
import logging

_LOGGER = logging.getLogger(__name__)

class ALBuffer(ALObject):
    _invalid_buffer: Optional[ALBuffer] = None
    _empty_buffer: Optional[ALBuffer] = None

    @classmethod
    def invalid(cls):
        if cls._invalid_buffer:
            return cls._invalid_buffer

        frequency = 21000
        data = np.linspace(0, 1.0, frequency, False, dtype=np.ubyte)

        cls._invalid_buffer = cls(SoundFormat.Mono8, data.tobytes(), frequency)
        return cls._invalid_buffer
    
    @classmethod
    def empty(cls):
        if cls._empty_buffer:
            return cls._empty_buffer
        
        cls._invalid_buffer = cls(SoundFormat.Mono8, b'', 21000)
        return cls._invalid_buffer

    def __init__(self, _format: SoundFormat, data: bytes, sample_rate: int):
        super().__init__()

        self.size = len(data)

        al.alGenBuffers(1, self._id)
        al.alBufferData(self._id, _format, data, self.size, sample_rate)

        _LOGGER.debug('%s created succesfully (data size: %.3fkB).', self, self.size / 1000.0)

    def _delete(self) -> None:
        al.alDeleteBuffers(1, self._id)
