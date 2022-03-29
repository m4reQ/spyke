import enum
from openal import al

class SourceState(enum.IntEnum):
    Initial = al.AL_INITIAL
    Paused = al.AL_PAUSED
    Playing = al.AL_PLAYING
    Stopped = al.AL_STOPPED

class SoundFormat(enum.IntEnum):
    Mono8 = al.AL_FORMAT_MONO8
    Mono16 = al.AL_FORMAT_MONO16
    Stereo8 = al.AL_FORMAT_STEREO8
    Stereo16 = al.AL_FORMAT_STEREO16