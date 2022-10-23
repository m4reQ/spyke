from pydub import AudioSegment
from spyke import debug, utils
from spyke.audio import ALBuffer
from spyke.enums import SoundFormat
from spyke.resources.types import Sound

from .loader import LoaderBase


def _get_format(channels: int, bitwidth: int) -> SoundFormat:
    enum_str = ('Mono' if channels == 1 else 'Stereo') + str(bitwidth)
    return getattr(SoundFormat, enum_str)

class SoundLoader(LoaderBase[Sound, AudioSegment]):
    __supported_extensions__ = ['.wav', '.mp3', '.ogg', '.flv']

    @staticmethod
    @debug.profiled('resources')
    def load_from_file(filepath: str) -> AudioSegment:
        _format = utils.get_extension_name(filepath)
        return AudioSegment.from_file(filepath, _format)

    @staticmethod
    @debug.profiled('resources')
    def finalize_loading(resource: Sound, loading_data: AudioSegment) -> None:
        _format = _get_format(loading_data.channels, loading_data.sample_width * 8)

        with resource.lock:
            resource.buffer = ALBuffer(_format, loading_data.raw_data, loading_data.frame_rate)
            resource.is_loaded = True
