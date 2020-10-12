import sys, os
oldOut = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
sys.stdout = oldOut

import OpenGL
OpenGL.ERROR_CHECKING = False

IS_NVIDIA = False

DEBUG_LOG_TIME = True
DEBUG_ENABLE = True
DEBUG_COLOR = False

from time import perf_counter
START_TIME = perf_counter()