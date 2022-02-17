from typing import Any
from spyke.audio import al
from openal import al as AL
import glm


class SoundSource(al.ALObject):
    def __init__(self):
        super().__init__()

        self._id = al.generate_source()
    
    def set_position(self, pos: glm.vec3) -> None:
        AL.alSource3f(self._id, AL.AL_POSITION, pos.x, pos.y, pos.z)
    
    def set_gain(self, gain: float) -> None:
        AL.alSourcef(self._id, AL.AL_GAIN, gain)
    
    def set_velocity(self, velocity: glm.vec3) -> None:
        AL.alSource3f(self._id, AL.AL_VELOCITY, velocity)
    
    def set_pitch(self, pitch: float) -> None:
        AL.alSourcef(self._id, AL.AL_PITCH, pitch)
    
    def set_looping(self, looping: bool) -> None:
        AL.alSourcei(self._id, AL.AL_LOOPING, 1 if looping else 0)
    
    def _delete(self) -> None:
        al.delete_source(self._id)
    
