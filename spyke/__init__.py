from spyke.application import Application
from spyke.graphics import WindowSpecs
from . import resourceManager as ResourceManager
from .constants import *
import sys

from spyke.exceptions import SpykeException
if sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 7):
    raise SpykeException(
        f'To run spyke you require python version at least 3.7 (currently using {sys.version_info.major}.{sys.version_info.minor}).')

import OpenGL
OpenGL.USE_ACCELERATE = True
OpenGL.FORWARD_COMPATIBLE_ONLY = True
OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING = True
OpenGL.ERROR_CHECKING = __debug__


def run(app: Application, run_editor: bool = False) -> None:
    if not __debug__ and run_editor:
        raise SpykeException(
            'You cannot run application in spyke editor with optimization enabled.')

    if run_editor:
        # TODO: Implement `Editor`
        editor = Editor(app=app)
        editor.run()
    else:
        app._run()

    sys.exit(0)
