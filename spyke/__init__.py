import sys, os
oldOut = sys.stdout
sys.stdout = open(os.devnull, 'w')
import pygame
sys.stdout = oldOut

import OpenGL
OpenGL.ERROR_CHECKING = False