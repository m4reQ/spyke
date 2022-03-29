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
    # TODO: Use better format detection
    if channels == 1:
        if bitwidth == 8:
            return SoundFormat.Mono8
        elif bitwidth == 16:
            return SoundFormat.Mono16
    elif channels == 2:
        if bitwidth == 8:
            return SoundFormat.Stereo8
        elif bitwidth == 16:
            return SoundFormat.Stereo16
    
    raise ValueError(f'Unknown format for sample width: {bitwidth} and channels count: {channels}')

class SoundLoader(Loader[_SoundData, Sound]):
    __extensions__: List[str] = ['WAV', 'MP3', 'OGG', 'FLV']
    __restype__: Type[Sound] = Sound

    def _load(self) -> None:
        _format = utils.get_extension_name(self.filepath)
        self._data = _SoundData(AudioSegment.from_file(self.filepath, _format))

    def finalize(self) -> Sound:
        if not self._check_data_valid(self._data):
            return Sound.invalid(self.id)

        audio_segment = self._data.audio_segment

        _format = _get_format(audio_segment.channels, audio_segment.sample_width * 8)
        buffer = ALBuffer(_format, audio_segment.raw_data, audio_segment.frame_rate)

        sound = Sound(self.id, self.filepath)
        sound.buffer = buffer

        return sound