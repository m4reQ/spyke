import logging

from openal import alc as ALC
from spyke import debug
from spyke.runtime import DisposableBase


class AudioDevice(DisposableBase):
    @debug.profiled('audio', 'initialization')
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

        _logger.debug('Audio device "%s" opened.', self.name)

    @debug.profiled('audio', 'cleanup')
    def _dispose(self) -> None:
        ALC.alcDestroyContext(self._context)
        ALC.alcCloseDevice(self._handle)

        _logger.debug('Audio device "%s" closed.', self.name)

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def context(self) -> int:
        return self._context

_logger = logging.getLogger(__name__)
