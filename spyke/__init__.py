from __future__ import annotations
import ctypes as ct
import inspect
import openal
import OpenGL
import sys

_PYTHON_MIN_VER = (3, 7)

if sys.version_info.major < _PYTHON_MIN_VER[0] or (sys.version_info.major >= _PYTHON_MIN_VER[0] and sys.version_info.minor < _PYTHON_MIN_VER[1]):
    raise SpykeException(
        f'To run spyke you require python version at least {_PYTHON_MIN_VER[0]}.{_PYTHON_MIN_VER[1]} (currently using {sys.version_info.major}.{sys.version_info.minor}).')

OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True
OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING = True
OpenGL.ERROR_CHECKING = __debug__
OpenGL.ERROR_ON_COPY = False

from . import debug
from spyke.application import Application
from spyke.exceptions import SpykeException
from spyke.windowing import WindowSpecs

openal.OAL_DONT_AUTO_INIT = True
# NOTE: We are loading openal in this messy way to remove unnecessary and expensive error checking.
if not __debug__:
    members = inspect.getmembers(
        openal.al, lambda x: isinstance(x, ct._CFuncPtr))
    members += inspect.getmembers(openal.alc,
                                  lambda x: isinstance(x, ct._CFuncPtr))
    for _, member in members:
        del member.errcheck


def run(app: Application, run_editor: bool = False) -> None:
    if not __debug__ and run_editor:
        raise SpykeException(
            'You cannot run application in spyke editor with optimization enabled.')

    if run_editor:
        # TODO: Implement editor

        raise NotImplementedError('Editor is not implemented yet.')
        # editor = Editor(app=app)
        # editor._run()
    else:
        app._run()

    sys.exit(0)
