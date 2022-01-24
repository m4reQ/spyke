import ctypes
import time
import numpy as np
from OpenGL import GL

START_TIME = time.perf_counter()

DEFAULT_LOG_FILENAME = "novaDefaultLog.log"
DEFAULT_ICON_FILEPATH = "branding/spykeIcon.ico"

DEFAULT_IMGUI_BG_COLOR = "#c9c6c5"
DEFAULT_IMGUI_HIGLIGHT_COLOR = "black"
DEFAULT_IMGUI_FONT = ("Helvetica", 9)
DEFAULT_IMGUI_TITLE_BG_COLOR = "#8c8c8c"

MAX_LOADING_TASKS_COUNT = 6

DEBUG_LOG_TO_FILE = True

_OPENGL_VER_MAJOR = 4
_OPENGL_VER_MINOR = 5

_GL_FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
_GL_INT_SIZE = ctypes.sizeof(ctypes.c_int)

_FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)
_INT_SIZE = ctypes.sizeof(ctypes.c_int)

_C_FLOAT_P = ctypes.POINTER(ctypes.c_float)
_C_INT_P = ctypes.POINTER(ctypes.c_int)

_NP_FLOAT = np.float32
_NP_DOUBLE = np.float64
_NP_BYTE = np.int8
_NP_UBYTE = np.uint8
_NP_SHORT = np.int16
_NP_USHORT = np.uint16
_NP_INT = np.int32
_NP_UINT = np.uint32
_NP_LONG = np.int64
_NP_ULONG = np.uint64

_QUAD_MODEL_INDEX = 0
_TRIANGLE_MODEL_INDEX = 1
_HEXAGON_MODEL_INDEX = 2

_IMAGE_FORMAT_MAP = {
    "JPEG": GL.GL_RGB,
    "JPG": GL.GL_RGB,
    "PNG": GL.GL_RGBA,
    "RGB": GL.GL_RGB,
    "RGBA": GL.GL_RGBA
}
