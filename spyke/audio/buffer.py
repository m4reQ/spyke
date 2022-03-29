from __future__ import annotations
from spyke.enums import SoundFormat
from spyke.audio import ALObject
from spyke import debug
from openal import al


class ALBuffer(ALObject):
    def __init__(self, _format: SoundFormat, data: bytes, sample_rate: int):
        super().__init__()

        self.size = len(data)

        al.alGenBuffers(1, self._id)
        al.alBufferData(self._id, _format, data, self.size, sample_rate)

        debug.log_info(f'{self} created succesfully (data size: {(self.size / 1000.0):.3f}kB).')

    def _delete(self) -> None:
        al.alDeleteBuffers(1, self._id)
