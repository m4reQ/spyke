import logging
import typing as t
from uuid import UUID

from spyke import resources
from spyke.audio import SoundSource
from spyke.ecs import Component
from spyke.enums import SourceState
from spyke.resources.types import Sound

_logger = logging.getLogger(__name__)

class AudioComponent(Component):
    def __init__(self, sound_id: t.Optional[UUID]=None):
        self.source: SoundSource = SoundSource()
        self.current_sound: t.Optional[Sound]

        if sound_id:
            self.set_sound(sound_id)

    def _check_sound_set(self) -> bool:
        if self.current_sound is None:
            _logger.warning('Audio component has no sound set. To play a sound first associate it with AudioComponent using set_sound method.')
            return False

        return True

    # TODO: Fix mypy errors related to lru_cache
    def set_sound(self, sound_id: UUID) -> None:
        sound = resources.get(sound_id, Sound)
        self.source.set_buffer(sound.buffer)
        self.current_sound = sound

    def play(self) -> None:
        if not self._check_sound_set() or self.source_state != SourceState.Playing:
            return

        self.source.play()

    def pause(self) -> None:
        if not self._check_sound_set() or self.source_state != SourceState.Playing:
            return

        self.source.pause()

    def stop(self) -> None:
        if not self._check_sound_set() or self.source_state != SourceState.Stopped:
            return

        self.source.stop()

    def rewind(self) -> None:
        self.source.rewind()

    @property
    def source_state(self) -> SourceState:
        return self.source.get_state()
