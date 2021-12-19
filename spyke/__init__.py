import sys
if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 7):
    raise RuntimeError(f'To run spyke you require python version at least 3.7 (currently using {sys.version_info.major}.{sys.version_info.minor}).')

import OpenGL
OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True
OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING = True
OpenGL.ERROR_CHECKING = True

from .constants import *
from . import resourceManager as ResourceManager