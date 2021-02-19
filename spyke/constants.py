import ctypes

START_TIME = 0.0

USE_FAST_ARRAY_MIN_FILTER = False
USE_FAST_NV_MULTISAMPLE = False

_MAIN_PROCESS = None
_GLFW_INITIALIZED = False

_GL_FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
_GL_INT_SIZE = ctypes.sizeof(ctypes.c_int)
_FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
_INT_SIZE = ctypes.sizeof(ctypes.c_int)