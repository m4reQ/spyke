from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from spyke.enums import TextureTarget
    from typing import List

from spyke import debug
from spyke.exceptions import GraphicsException
from OpenGL import GL
from abc import ABC, abstractmethod


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


class GLObject(ABC):
    _objects: List[GLObject] = []

    @staticmethod
    def delete_all() -> None:
        cnt = len(GLObject._objects)

        for obj in GLObject._objects:
            obj._delete()

        GLObject._objects.clear()

        debug.log_info(f'{cnt} OpenGL objects have been deleted.')

    def __init__(self):
        self._id: GL.GLint = GL.GLint(-1)
        self._deleted: bool = False

        GLObject._objects.append(self)

    def __str__(self):
        return f'{type(self).__name__} (id: {self._id.value})'

    def __repr__(self):
        return str(self)

    def _delete(self) -> None:
        if self._deleted:
            return

        self.delete()

        GLObject._objects.remove(self)
        self._deleted = True
        debug.log_info(f'{self} deleted succesfully.')

    @abstractmethod
    def delete(self) -> None:
        pass

    @property
    def id(self) -> int:
        if __debug__:
            if self._id.value == -1:
                raise GraphicsException(
                    f'Tried to use uninitialized OpenGL object of type {type(self).__name__}.')

            if self._deleted:
                raise GraphicsException(
                    'Tried to use OpenGL object that is already deleted.')

        return self._id.value
