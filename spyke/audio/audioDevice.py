import logging
from openal import alc as ALC


class AudioDevice:
    def __init__(self):
        self._handle: int = ALC.alcOpenDevice(None)
        assert self._handle, 'Cannot open sound device'

        self._context: int = ALC.alcCreateContext(self._handle, None)
        assert self._context, 'Cannot create audio context'

        assert ALC.alcMakeContextCurrent(
            self._context), 'Cannot make audio context current'

        self.name: str = ALC.alcGetString(
            self._handle, ALC.ALC_DEVICE_SPECIFIER).decode('utf-8')

        logging.log(logging.SP_INFO, f'Audio device "{self.name}" opened.')

    def close(self) -> None:
        ALC.alcDestroyContext(self._context)
        ALC.alcCloseDevice(self._handle)

        logging.log(logging.SP_INFO, f'Audio device "{self.name}" closed.')

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def context(self) -> int:
        return self._context