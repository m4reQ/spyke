from spyke.enums import SoundFormat
from spyke.audio import al
from spyke import debug
from openal import al as AL


class SoundBuffer(al.ALObject):
    def __init__(self, _format: SoundFormat, data: bytes, sample_rate: int):
        super().__init__()

        self._id = al.generate_buffer()
        self.size = len(data)
        AL.alBufferData(self._id, _format, data, self.size, sample_rate)

        debug.log_info(
            f'{self} created succesfully (data size: {self.size / 1024.0}kB).')

    def delete(self) -> None:
        al.delete_buffer(self._id)
