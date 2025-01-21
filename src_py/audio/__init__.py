import inspect
import ctypes as ct

import openal

from .al import ALObject
from .buffer import ALBuffer
from .context import AudioDevice
from .source import SoundSource

__all__ = [
    'ALObject',
    'ALBuffer',
    'AudioDevice',
    'SoundSource',
]

def _setup_openal_lib() -> None:
    openal.OAL_DONT_AUTO_INIT = True
    
    if not __debug__:
        return
    
    # NOTE: We are loading openal in this messy way to remove unnecessary and expensive error checking.
    members = inspect.getmembers(openal.al, lambda x: isinstance(x, ct._CFuncPtr)) #type: ignore
    members += inspect.getmembers(openal.alc, lambda x: isinstance(x, ct._CFuncPtr)) # type: ignore

    for _, member in members:
        del member.errcheck

_setup_openal_lib()
