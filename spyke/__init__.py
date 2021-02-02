import sys
if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 7):
    raise RuntimeError(f"To run sPYke you require python version at least 3.7 (currently using {sys.version_info.major}.{sys.version_info.minor}).")

from .constants import START_TIME, _MAIN_PROCESS

from time import perf_counter
START_TIME = perf_counter()

import os, psutil
_MAIN_PROCESS = psutil.Process(os.getpid())

oldOut = sys.stdout
with open(os.devnull, "w") as f:
    sys.stdout = f
    import pygame
    sys.stdout = oldOut

import OpenGL
OpenGL.ERROR_CHECKING = False
OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True

import glfw
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
handle = glfw.create_window(1, 1, "", None, None)
glfw.make_context_current(handle)

from .graphics import contextInfo
contextInfo.ContextInfo.TryGetInfo()

glfw.set_window_should_close(handle, glfw.TRUE)
glfw.destroy_window(handle)
glfw.window_hint(glfw.VISIBLE, glfw.TRUE)