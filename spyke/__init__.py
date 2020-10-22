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

IS_NVIDIA = False

DEBUG_LOG_TIME = True
DEBUG_ENABLE = True
DEBUG_COLOR = False

USE_FAST_MIN_FILTER = False

USE_TIMED_GC = True
GC_TIMEOUT = 1