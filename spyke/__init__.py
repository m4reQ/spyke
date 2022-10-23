import sys

from spyke import debug

debug.initialize()

from spyke import events, exceptions, graphics, resources, utils

from .application import *
from .windowing import *

__all__ = [
    'debug',
    'graphics',
    'utils',
    'resources',
    'events',
    'Application',
    'Window',
    'WindowSpecs',
    'exceptions'
]

_PYTHON_MIN_VER = (3, 10)

ver = sys.version_info
if ver < _PYTHON_MIN_VER:
    raise RuntimeError(f'Spyke requires python version to be at least {_PYTHON_MIN_VER[0]}.{_PYTHON_MIN_VER[1]} (currently using {ver.major}.{ver.minor}).')
