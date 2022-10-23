import logging
from OpenGL import GL

from spyke.enums import DebugSeverity, DebugSource, DebugType
from spyke.exceptions import GraphicsException

def opengl_debug_callback(source: int, msg_type: int, _, severity: int, __, raw: bytes, ___) -> None:
    logger = logging.getLogger(__name__)

    _source = DebugSource(source).name.upper()
    _msg_type = DebugType(msg_type).name.upper()
    _severity = DebugSeverity(severity)

    message_formatted = f'OpenGL {_source} -> {_msg_type}: {raw.decode("ansi")}.'

    if _severity == DebugSeverity.High:
        raise GraphicsException(message_formatted)
    elif _severity == DebugSeverity.Medium:
        logger.warning(message_formatted)
    elif _severity in [DebugSeverity.Low, DebugSeverity.Notification]:
        logger.info(message_formatted)

def get_gl_error() -> None:
    err = GL.glGetError()
    if err != GL.GL_NO_ERROR:
        raise GraphicsException(err)
