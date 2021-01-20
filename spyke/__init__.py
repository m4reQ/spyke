import sys
if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 7):
    raise RuntimeError(f"To run sPYke you require python version at least 3.7 (currently using {sys.version_info.major}.{sys.version_info.minor}).")

from time import perf_counter
START_TIME = perf_counter()

DEBUG_LOG_TIME = True
DEBUG_ENABLE = True
DEBUG_COLOR = False
AUTO_LOG_EXCEPTIONS = True

USE_FAST_ARRAY_MIN_FILTER = False
USE_FAST_NV_MULTISAMPLE = False

USE_TIMED_GC = False
GC_TIMEOUT = 1

import os, psutil
_PROCESS = psutil.Process(os.getpid())

oldOut = sys.stdout
with open(os.devnull, "w") as f:
    sys.stdout = f
    import pygame
    sys.stdout = oldOut

import OpenGL
#OpenGL.ERROR_CHECKING = False
OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True

import glfw
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
handle = glfw.create_window(1, 1, "", None, None)
glfw.make_context_current(handle)
from OpenGL import GL
vendorStr = GL.glGetString(GL.GL_VENDOR).decode("ASCII").lower()

if "nvidia" in vendorStr:
    IS_NVIDIA = True
else:
    IS_NVIDIA = False

glfw.set_window_should_close(handle, glfw.TRUE)
glfw.destroy_window(handle)
glfw.window_hint(glfw.VISIBLE, glfw.TRUE)