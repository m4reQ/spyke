from __future__ import annotations
import logging
from spyke.audio import ALObject
from spyke.audio import ALBuffer
from spyke.enums import SourceState
from openal import al, ALuint, ALint
import glm

_LOGGER = logging.getLogger(__name__)

class SoundSource(ALObject):
    def __init__(self):
        super().__init__()

        self._current_buffer_id: ALuint = ALuint()

        al.alGenSources(1, self._id)

        _LOGGER.debug('%s created succesfully.', self)
    
    def set_position(self, pos: glm.vec3) -> None:
        al.alSource3f(self.id, al.AL_POSITION, pos.x, pos.y, pos.z)
    
    def set_gain(self, gain: float) -> None:
        al.alSourcef(self.id, al.AL_GAIN, gain)
    
    def set_velocity(self, velocity: glm.vec3) -> None:
        al.alSource3f(self.id, al.AL_VELOCITY, velocity.x, velocity.y, velocity.z)
    
    def set_pitch(self, pitch: float) -> None:
        al.alSourcef(self.id, al.AL_PITCH, pitch)
    
    def set_looping(self, looping: bool) -> None:
        al.alSourcei(self.id, al.AL_LOOPING, 1 if looping else 0)
    
    def play(self) -> None:
        al.alSourcePlay(self.id)

    def pause(self) -> None:
        al.alSourcePause(self.id)
    
    def stop(self) -> None:
        al.alSourceStop(self.id)
    
    def rewind(self) -> None:
        al.alSourceRewind(self.id)

    def set_buffer(self, buffer: ALBuffer) -> None:
        if self._current_buffer_id == buffer.id:
            return

        al.alSourcei(self.id, al.AL_BUFFER, buffer.id)
        self._current_buffer_id = buffer.id
    
    def set_state(self, state: SourceState) -> None:
        al.alSourcei(self.id, al.AL_SOURCE_STATE, state)
    
    def get_state(self) -> SourceState:
        state = ALint()
        al.alGetSourcei(self.id, al.AL_SOURCE_STATE, state)

        return SourceState(state.value)
    
    def _delete(self) -> None:
        al.alSourcei(self.id, al.AL_BUFFER, 0)
        al.alDeleteSources(1, self._id)