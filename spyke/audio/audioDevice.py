from .buffer import ALBuffer
from openal import alc as ALC
import logging

_LOGGER = logging.getLogger(__name__)

class AudioDevice:
    def __init__(self):
        super().__init__()
        self._handle: int = ALC.alcOpenDevice(None)
        assert self._handle, 'Cannot open sound device'

        self._context: int = ALC.alcCreateContext(self._handle, None)
        assert self._context, 'Cannot create audio context'

        assert ALC.alcMakeContextCurrent(
            self._context), 'Cannot make audio context current'

        self.name: str = ALC.alcGetString(
            self._handle, ALC.ALC_DEVICE_SPECIFIER).decode('utf-8')

        _LOGGER.debug('Audio device "%s" opened.', self.name)
    
    def close(self) -> None:
        if ALBuffer._empty_buffer:
            ALBuffer._empty_buffer.delete()
        if ALBuffer._invalid_buffer:
            ALBuffer._invalid_buffer.delete()

        ALC.alcDestroyContext(self._context)
        ALC.alcCloseDevice(self._handle)

        _LOGGER.debug('Audio device "%s" closed.', self.name)

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def context(self) -> int:
        return self._context
