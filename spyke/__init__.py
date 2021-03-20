import sys
if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 7):
    raise RuntimeError(f"To run spyke you require python version at least 3.7 (currently using {sys.version_info.major}.{sys.version_info.minor}).")

from .constants import START_TIME, _MAIN_PROCESS
from time import perf_counter
import os, psutil

import OpenGL
OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True
OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING = True
#OpenGL.ERROR_CHECKING = False

import glfw

def Init():
    global START_TIME, _MAIN_PROCESS

    START_TIME = perf_counter()
    _MAIN_PROCESS = psutil.Process(os.getpid())
    
    if __debug__:
        from .debugging import Debug, LogLevel
        Debug._Init()

        Debug.Log(f"Engine initialized in {perf_counter() - START_TIME} seconds.", LogLevel.Info)