import datetime
import ctypes

START_TIME = 0.0

DEBUG_LOG_TIME = True
DEBUG_ENABLE = True
DEBUG_COLOR = False

AUTO_LOG_EXCEPTIONS = True

PROFILE_ENABLE = True

USE_FAST_ARRAY_MIN_FILTER = False
USE_FAST_NV_MULTISAMPLE = False

_MAIN_PROCESS = None
_START_EPOCH_TIME = datetime.datetime(1970, 1, 1)
_GL_FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
_INT_SIZE = ctypes.sizeof(ctypes.c_int)