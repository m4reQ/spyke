from .buffer import SoundBuffer
from .audioLoader import LoadSound
from ..debugging import Debug, LogLevel

class BufferManager(object):
    Buffers = {}

    @staticmethod
    def AddBuffer(name: str, buffer: SoundBuffer):
        if name in BufferManager.Buffers.keys():
            if buffer != BufferManager.Buffers[name]:
                Debug.Log(f"Buffer '{name}' (id: {BufferManager.Buffers[name].ID}) overwritten with buffer with id {buffer.ID}", LogLevel.Warning)

                BufferManager.Buffers[name] = buffer
        
        BufferManager.Buffers[name] = buffer
    
    @staticmethod
    def CreateBuffer(filepath: str):
        BufferManager.AddBuffer(filepath, SoundBuffer(LoadSound(filepath)))
    
    @staticmethod
    def GetBuffer(name: str):
        if not name in BufferManager.Buffers:
            raise RuntimeError(f"Buffer named '{name}' not found.")

        return BufferManager.Buffers[name]
    
    @staticmethod
    def HasBuffer(name: str):
        return name in BufferManager.Buffers
