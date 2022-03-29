from __future__ import annotations
from spyke.enums import SourceState
from spyke import debug, resources
from spyke.resources import Sound
from spyke.audio import SoundSource
from .component import Component
from typing import Optional
from uuid import UUID

class AudioComponent(Component):
    def __init__(self, sound_id: Optional[UUID]=None):
        self.source: SoundSource = SoundSource()
        self.current_sound: Optional[Sound]

        if sound_id:
            self.set_sound(sound_id)
    
    def _check_sound_set(self) -> bool:
        if self.current_sound is None:
            debug.log_warning('Audio component has no sound set. To play a sound first associate it with AudioComponent using set_sound method.')
            return False
        
        return True
        
    def set_sound(self, sound_id: UUID) -> None:
        sound = resources.get(sound_id)
        assert isinstance(sound, Sound), f'UUID: {sound} points to a resource of type: {type(sound)}. Expected type: {Sound.__name__}.'

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
