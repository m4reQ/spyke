import abc

from OpenGL import GL

from spyke.enums import TextureTarget
from spyke.utils import Deletable

def create_program() -> GL.GLint:
    return GL.GLint(GL.glCreateProgram())

def create_texture(target: TextureTarget) -> GL.GLint:
    _id = GL.GLint()
    GL.glCreateTextures(target, 1, _id)

    return _id

def create_vertex_array() -> GL.GLint:
    _id = GL.GLint()
    GL.glCreateVertexArrays(1, _id)

    return _id

def create_buffer() -> GL.GLint:
    _id = GL.GLint()
    GL.glCreateBuffers(1, _id)

    return _id

def create_framebuffer() -> GL.GLint:
    _id = GL.GLint()
    GL.glCreateFramebuffers(1, _id)

    return _id

class GLObject(Deletable, abc.ABC):
    def __init__(self):
        super().__init__()
        self._id: GL.GLint = GL.GLint(0)

    def __str__(self):
        return f'{type(self).__name__} (id: {self._id.value})'

    def __repr__(self):
        return str(self)

    @property
    def id(self) -> int:
        assert self._id.value != 0, f'Tried to use uninitialized OpenGL object: {self}.'
        assert not self._deleted, f'Tried to use OpenGL object that is already deleted: {self}.'

        return self._id.value
