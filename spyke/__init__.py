from __future__ import annotations
import ctypes as ct
import inspect
import openal
import OpenGL
import typing
if typing.TYPE_CHECKING:
    from spyke.application import Application
    from spyke.editor import Editor

import sys
from . import debug

_PYTHON_MIN_VERSION = (3, 7)

if sys.version_info.major < _PYTHON_MIN_VERSION[0] or (sys.version_info.major >= _PYTHON_MIN_VERSION[0] and sys.version_info.minor < _PYTHON_MIN_VERSION[1]):
    from spyke.exceptions import SpykeException
    raise SpykeException(
        f'To run spyke you require python version at least {_PYTHON_MIN_VERSION[0]}.{_PYTHON_MIN_VERSION[1]} (currently using {sys.version_info.major}.{sys.version_info.minor}).')

OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True
OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING = True
OpenGL.ERROR_CHECKING = __debug__
OpenGL.ERROR_ON_COPY = False


def _err_check(result, func, args):
    return result


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
        editor = Editor(app=app)
        editor._run()
    else:
        app._run()

    sys.exit(0)
