from .soundData import SoundData
from ..utils import ObjectManager

import openal

class SoundBuffer(object):
    def __init__(self, data: SoundData):
        self.handle = openal.Buffer(data.Format, data.Data, data.Length, data.SampleRate)
        self.data = data

        ObjectManager.AddObject(self)

    def Delete(self):
        self.handle.destroy()

    @property
    def ID(self):
        return self.handle.id