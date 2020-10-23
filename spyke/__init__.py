import sys
version = sys.version_info
if version.major < 3:
    raise RuntimeError(f"To run sPYke you require python version at least 3.7 (currently using {version.major}.{version.minor}).")
if version.major >= 3 and version.minor < 7:
    raise RuntimeError(f"To run sPYke you require python version at least 3.7 (currently using {version.major}.{version.minor}).")

from time import perf_counter
START_TIME = perf_counter()

import sys, os
oldOut = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
sys.stdout = oldOut

import psutil
_PROCESS = psutil.Process(os.getpid())

import OpenGL
OpenGL.ERROR_CHECKING = False
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
glfw.terminate()

DEBUG_LOG_TIME = True
DEBUG_ENABLE = True
DEBUG_COLOR = False

USE_FAST_MIN_FILTER = False

USE_TIMED_GC = True
GC_TIMEOUT = 1