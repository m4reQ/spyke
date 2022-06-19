import typing as t

from pydub import AudioSegment

from spyke.audio import ALBuffer
from spyke.enums import SoundFormat
from spyke.resources.types import Sound
from spyke import utils, debug
from .loader import LoaderBase

def _get_format(channels: int, bitwidth: int) -> SoundFormat:
    enum_str = ('Mono' if channels == 1 else 'Stereo') + str(bitwidth)
    return getattr(SoundFormat, enum_str)

class SoundLoader(LoaderBase[Sound]):
    @staticmethod
    def get_suitable_extensions() -> t.List[str]:
        return ['.wav', '.mp3', '.ogg', '.flv']

    @debug.profiled('resources')
    def load(self, filepath: str) -> t.Any:
        _format = utils.get_extension_name(filepath)
        return AudioSegment.from_file(filepath, _format)

    @debug.profiled('resources')
    def finish_loading(self) -> None:
        data: AudioSegment = self.loading_data

        _format = _get_format(data.channels, data.sample_width * 8)
        self.resource.buffer = ALBuffer(_format, data.raw_data, data.frame_rate)
