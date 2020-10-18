from time import perf_counter
START_TIME = perf_counter()

import sys, os
oldOut = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
sys.stdout = oldOut

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