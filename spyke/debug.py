from OpenGL.GL import glGetError, GL_NO_ERROR

import time

ENABLED = False
LOG_TIME = False

START_TIME = time.perf_counter()

class LogLevel:
    Info = "INFO"
    Warning = "WARNING"
    Error = "ERROR"

def Enable():
    global ENABLED
    ENABLED = True

def LogTime():
    global LOG_TIME
    LOG_TIME = True

def Log(msg, logLevel: LogLevel):
    global ENABLED
    if ENABLED:
        if LOG_TIME:
            print(f"[{logLevel}][{(time.perf_counter() - START_TIME):.3F}s] {msg}")
        else:
            print(f"[{logLevel}] {msg}")

def GetGLError():
    err = glGetError()
    if err != GL_NO_ERROR:
        Log(err, LogLevel.Error)

class Timer:
    __Start = 0.0
    
    @staticmethod
    def Start():
        Timer.__Start = time.perf_counter()
    
    @staticmethod
    def Stop():
        return time.perf_counter() - Timer.__Start
    
    @staticmethod
    def GetCurrent():
        return time.perf_counter()