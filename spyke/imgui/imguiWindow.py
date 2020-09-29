from ..debug import Log, LogLevel

import tkinter
import threading

class ImguiWindow(object):
    LocalTkinterLock = threading.RLock()

    def __init__(self, imInstance, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.isRunning = False
        self.thread = threading.Thread(target = self.__Run)

        self.__handle = None

        self.imInstance = imInstance

        self.mousePos = (0, 0)
    
    def OnFrame(self):
        pass

    def Setup(self):
        pass

    def Close(self):
        self.isRunning = False

    def __Run(self):
        self.isRunning = True

        self.__handle = tkinter.Tk()

        self.__handle.protocol("WM_DELETE_WINDOW", self.Close)
        self.__handle.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
        self.__handle.bind("<B1-Motion>", self.__GetMousePos)

        self.Setup()

        Log("Imgui window started.", LogLevel.Info)

        while self.isRunning:
            self.OnFrame()

            try:
                self.__handle.update()
            except tkinter.TclError:
                pass

        try:
            self.__handle.destroy()
        except tkinter.TclError:
            pass
    
        Log("Imgui window closed.", LogLevel.Info)
    
    def __GetMousePos(self, event):
        self.mousePos = (event.x, event.y)
    
    def Move(self, x, y):
        self.x = x
        self.y = y

        ImguiWindow.LocalTkinterLock.acquire()
        self.__handle.geometry(f"+{self.x}+{self.y}")
        ImguiWindow.LocalTkinterLock.release()
    
    def Resize(self, width, height):
        self.width = width
        self.height = height

        ImguiWindow.LocalTkinterLock.acquire()
        self.__handle.geometry(f"{self.width}x{self.height}")
        ImguiWindow.LocalTkinterLock.release()
    
    @property
    def Handle(self):
        return self.__handle