import spyke
spyke.Init()

from spyke import ResourceManager
from spyke.window import *

import time

class Test(GlfwWindow):
    def __init__(self):
        spec = WindowSpecs(512, 512, "")

        self.testsCount = 5
        
        super().__init__(spec)
    
    def OnLoad(self):
        start = time.perf_counter()

        for _ in range(self.testsCount):
            ResourceManager.CreateTexture("tests/test1.jpg")
        
        ResourceManager.FinishLoading()
        
        print(f"Loaded in {time.perf_counter() - start} seconds with {self.testsCount} texture loads.")

        raise

if __name__ == "__main__":
    t = Test()
    t.Run()