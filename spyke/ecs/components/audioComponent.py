from ...audio.sound import Sound

class AudioComponent(object):
    def __init__(self, filepath: str):
        self.paused = False
        self.looping = False
        self.ended = False
        self.point = 0.0
        self.__handle = Sound(filepath)
        self.length = self.__handle.data.LengthSeconds

    def OnUpdate(self, deltaTime: float):
        if self.paused:
            return

        if not self.paused:
            self.point += deltaTime
        
        if self.point >= self.length:
            if self.looping:
                self.point = 0.0
            else:
                self.paused = True
                self.ended = True
    
    def Pause(self):
        self.__handle.Pause()
        self.paused = True
    
    def Play(self):
        if self.paused:
            self.__handle.Play()

        self.paused = False
    
    def Stop(self):
        self.__handle.Stop()
        self.paused = True
        self.point = 0.0
    
    def HasEnded(self):
        if self.looping:
            return False
        
        return self.ended
    
