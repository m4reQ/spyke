import functools
import logging
import os
import time
import typing as t

from OpenGL import GL
import glfw
import colorama

from spyke import paths
from spyke.enums import DebugSeverity, DebugSource, DebugType
from spyke.exceptions import GraphicsException

__all__ = [
    'get_gl_error',
    'require_context',
    'timed',
    'debug_only',
    'require_context'
]


