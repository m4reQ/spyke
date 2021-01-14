from .bufferManager import BufferManager
from .buffer import SoundBuffer
from .audioLoader import LoadSound
from ..managers.objectManager import ObjectManager

import openal

class Sound(object):
    def __init__(self, filename: str):
        if not BufferManager.HasBuffer(filename):
            self.buffer = SoundBuffer(LoadSound(filename))
            BufferManager.AddBuffer(filename, self.buffer)
        else:
            self.buffer = BufferManager.GetBuffer(filename)

        self.data = self.buffer.data
        
        self.length = self.buffer.data.LengthSeconds
        self.__source = openal.Source(self.buffer.handle)

        ObjectManager.AddObject(self)
    
    def Delete(self):
        self.__source.destroy()

    def Play(self):
        self.__source.play()
    
    def Pause(self):
        self.__source.pause()
    
    def Stop(self):
        self.__source.stop()
    
    def Rewind(self):
        self.__source.rewind()
    
    def SetVolume(self, value: float):
        self.__source.set_gain(value)

    def GetState(self):
        return self.__source.get_state()
    
    @property
    def Volume(self):
        return self.__source.get(openal.AL_GAIN)
