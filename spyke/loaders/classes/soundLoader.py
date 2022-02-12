from spyke.audio import SoundBuffer
from spyke.enums import SoundFormat
from spyke.loaders import Loader
from pydub import AudioSegment


class SoundLoader(Loader):
    __restypes__ = ['MP3', 'OGG', 'AAC', 'WAV', 'MP4', 'WMA', 'FLV']

    def load(self, filepath: str, _format: str) -> AudioSegment:
        return AudioSegment.from_file(filepath, _format)

    def finalize(self, audio_segment: AudioSegment) -> SoundBuffer:
        channels = audio_segment.channels
        width = audio_segment.sample_width * 8
        _format: SoundFormat
        if channels == 1:
            if width == 8:
                _format = SoundFormat.Mono8
            elif width == 16:
                _format = SoundFormat.Mono16
        elif channels == 2:
            if width == 8:
                _format = SoundFormat.Stereo8
            elif width == 16:
                _format = SoundFormat.Stereo16

        assert _format is not None, f'Unknown format for sample width: {width} and channels count: {channels}'

        return SoundBuffer(_format, audio_segment.raw_data, audio_segment.frame_rate)
