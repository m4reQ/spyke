from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.application import Application
    from spyke.editor import Editor

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
OpenGL.ERROR_ON_COPY = False


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
