from __future__ import annotations
from spyke.audio import ALBuffer
from spyke.enums import SoundFormat
from spyke.resources.types import Sound
from .loader import Loader, LoadingData
from spyke import utils
from typing import List, Type
from pydub import AudioSegment
from dataclasses import dataclass

@dataclass
class _SoundData(LoadingData):
    audio_segment: AudioSegment

def _get_format(channels: int, bitwidth: int) -> SoundFormat:
    enum_str = ('Mono' if channels == 1 else 'Stereo') + str(bitwidth)

    return getattr(SoundFormat, enum_str)

class SoundLoader(Loader[_SoundData, Sound]):
    __extensions__: List[str] = ['WAV', 'MP3', 'OGG', 'FLV']
    __restype__: Type[Sound] = Sound

    def _load(self) -> None:
        _format = utils.get_extension_name(self.filepath)
        self._data = _SoundData(AudioSegment.from_file(self.filepath, _format))

    def finalize(self) -> None:
        if self.had_loading_error:
            with self.resource.lock:
                self.resource.is_invalid = True
                self.resource.buffer = ALBuffer.invalid()
            
            return

        audio_segment = self._data.audio_segment

        _format = _get_format(audio_segment.channels, audio_segment.sample_width * 8)
        buffer = ALBuffer(_format, audio_segment.raw_data, audio_segment.frame_rate)

        with self.resource.lock:
            self.resource.buffer = buffer