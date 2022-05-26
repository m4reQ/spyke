import logging
import typing as t
import functools

import numpy as np
import glm
from OpenGL import GL

from spyke.enums import ShaderType
from spyke.exceptions import GraphicsException, SpykeException
from spyke.graphics import gl

_logger = logging.getLogger(__name__)

class Shader(gl.GLObject):
    def __init__(self):
        super().__init__()

        self._id = gl.create_program()

        self.uniforms = {}
        self._stages = []

        self._compiled = False

    def add_stage(self, stage: ShaderType, filepath: str) -> None:
        if self._compiled:
            _logger.warning('Tried to add shader stage to already compiled shader.')
            return

        try:
            with open(filepath, "r") as f:
                source = f.read()
        except FileNotFoundError as e:
            raise SpykeException(
                f'Cannot find shader file named "{e.filename}"')

        shader = GL.glCreateShader(stage)
        self._stages.append(shader)

        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)

        info_log = GL.glGetShaderInfoLog(shader)
        assert len(info_log) == 0, f'{self} compilation error:\n{info_log.decode("ansi")}.'

        GL.glAttachShader(self.id, shader)

    def compile(self) -> None:
        if self._compiled:
            _logger.warning('%s is already compiled.', self)
            return

        GL.glLinkProgram(self.id)

        for stage in self._stages:
            GL.glDetachShader(self.id, stage)
            GL.glDeleteShader(stage)

        self._stages.clear()
        self._compiled = True

        _logger.debug('%s compiled succesfully.', self)

    def validate(self) -> None:
        if not self._compiled:
            _logger.error('Cannot validate not compiled shader program.')
            return

        GL.glValidateProgram(self.id)

        info_log = GL.glGetProgramInfoLog(self.id)
        assert len(info_log) == 0, f'{self} validation failure:\n{info_log.decode("ansi")}.'

        _logger.debug('%s has been validated succesfully.', self)

    def use(self) -> None:
        GL.glUseProgram(self.id)

    def _delete(self) -> None:
        GL.glDeleteProgram(self.id)

    @functools.lru_cache
    def get_attrib_location(self, name: str) -> int:
        loc = GL.glGetAttribLocation(self.id, name)
        assert loc != -1, f'Cannot find attribute named "{name}".'

        return loc

    def get_uniform_location(self, name: str) -> int:
        if name in self.uniforms:
            return self.uniforms[name]

        loc = GL.glGetUniformLocation(self.id, name)
        assert loc != -1, f'Cannot find uniform named "{name}".'

        self.uniforms[name] = loc

        return loc

    @functools.lru_cache
    def get_uniform_block_location(self, name: str) -> int:
        loc = GL.glGetUniformBlockIndex(self.id, name)
        assert loc != -1, f'Cannot find uniform block named "{name}".'

        return loc

    def set_uniform_block_binding(self, name: str, index: int) -> None:
        loc = self.get_uniform_block_location(name)
        GL.glUniformBlockBinding(self.id, loc, index)

    def set_uniform_int(self, name: str, value: t.Union[int, t.List[int]]) -> None:
        loc = self.get_uniform_location(name)

        if isinstance(value, int):
            GL.glProgramUniform1i(self.id, loc, value)
        elif isinstance(value, list):
            GL.glProgramUniform1iv(self.id, loc, len(
                value), np.asarray(value, dtype=np.int32))
        else:
            raise GraphicsException(f'Invalid type of uniform value: {type(value).__name__}')

    def set_uniform_float(self, name: str, value: t.Union[float, t.List[float]]) -> None:
        loc = self.get_uniform_location(name)

        if isinstance(value, int):
            GL.glProgramUniform1f(self.id, loc, value)
        elif isinstance(value, list):
            GL.glProgramUniform1fv(self.id, loc, len(
                value), np.asarray(value, dtype=np.float32))
        else:
            raise GraphicsException(f'Invalid type of uniform value: {type(value).__name__}')

    def set_uniform_double(self, name: str, value: t.Union[float, t.List[float]]) -> None:
        loc = self.get_uniform_location(name)

        if isinstance(value, int):
            GL.glProgramUniform1d(self.id, loc, value)
        elif isinstance(value, list):
            GL.glProgramUniform1dv(self.id, loc, len(
                value), np.asarray(value, dtype=np.float64))
        else:
            raise GraphicsException(f'Invalid type of uniform value: {type(value).__name__}')

    # TODO: Add generic typing for `value` parameter
    # TODO: Add support for matrices which width and height differ
    def set_uniform_matrix(self, name: str, value, transpose: bool) -> None:
        # TODO: Implement faster way of getting appropreriate function (maybe caching?)
        fn = getattr(GL, f'glProgramUniformMatrix{value.length}fv')

        fn(self.id, self.get_uniform_location(name),
           1, transpose, glm.value_ptr(value))
