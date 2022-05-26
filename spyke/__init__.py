import ctypes as ct
import inspect
import sys
import logging

import OpenGL
import openal

__all__ = [
    'debug',
    'graphics',
    'utils',
    'resources',
    'events',
    'Application',
    'Window',
    'WindowSpecs',
    'SpykeException',
    'GraphicsException',
    'run'
]

OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True
OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING = True
OpenGL.ERROR_CHECKING = __debug__
OpenGL.ERROR_ON_COPY = False

openal.OAL_DONT_AUTO_INIT = True

from . import debug
from . import utils
from . import graphics
from . import resources
from . import events
from .application import *
from .windowing import *
from .exceptions import *

_PYTHON_MIN_VER = (3, 7)

def _disable_openal_error_check() -> None:
    # NOTE: We are loading openal in this messy way to remove unnecessary and expensive error checking.
    members = inspect.getmembers(openal.al, lambda x: isinstance(x, ct._CFuncPtr)) #type: ignore
    members += inspect.getmembers(openal.alc, lambda x: isinstance(x, ct._CFuncPtr)) # type: ignore

    for _, member in members:
        del member.errcheck

def _check_python_version_valid() -> None:
    if sys.version_info.major < _PYTHON_MIN_VER[0] or (sys.version_info.major >= _PYTHON_MIN_VER[0] and sys.version_info.minor < _PYTHON_MIN_VER[1]):
        raise SpykeException(
            f'To run spyke you require python version at least {_PYTHON_MIN_VER[0]}.{_PYTHON_MIN_VER[1]} (currently using {sys.version_info.major}.{sys.version_info.minor}).')

def run(app: Application, run_editor: bool = False) -> None:
    debug.init()
    resources.init()

    logger = logging.getLogger(__name__)
    logger.info('Engine started.')

    if __debug__:
        logger.warning('Engine running in non-optimized mode. All graphics operations will be considerably slower.')

    _check_python_version_valid()

    if not __debug__:
        _disable_openal_error_check()

    if run_editor:
        if not __debug__:
            raise SpykeException('You cannot run application in spyke editor with optimization enabled.')

        logger.info('Engine running with editor application enabled.')
        # TODO: Implement editor

        raise NotImplementedError('Editor is not implemented yet.')
        # editor = Editor(app=app)
        # editor._run()
    else:
        app._run()

    logger.info('Engine shut down.')
    sys.exit(0)
