from ..utils import Abstract

class Window(Abstract):
    def Run(self) -> None:
        pass
    
    def OnFrame(self) -> None:
        pass

    def OnClose(self) -> None:
        pass

    def SetTitle(self, title: str) -> None:
        pass

    def SwapBuffers(self) -> None:
        pass

    def SetVsync(self, value: bool) -> None:
        pass