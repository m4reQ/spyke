import functools
import logging
import os
import typing as t
from concurrent import futures

import glm
import numpy as np
import numpy.typing as npt
from OpenGL import GL
from spyke import debug
from spyke.enums import ShaderType
from spyke.exceptions import SpykeException
from spyke.graphics.opengl_object import OpenglObjectBase

_ENCODING = 'ansi'

@t.final
class Shader(OpenglObjectBase):
    @classmethod
    def create(cls, stages: dict[ShaderType, str], binary_filepath: str | None = None):
        '''
        Creates shader program using given stages specification. If `binary_filepath`
        is provided, it tries to use already existing binary file to speed up shader
        program creation.
        It is recommended to use this function instead of creating `Shader` object directly,
        as it internally handles some errors that may be encountered while setting everything
        up manually.

        @stages: Dictionary of shader stages to include in program.
        @binary_filepath: Path to a file that contains compiled program binary.
        '''

        if binary_filepath is not None:
            if os.path.exists(binary_filepath):
                if _binary_formats_supported():
                    return cls(binary_filepath, False)

                _logger.warning('Cannot use provided shader binary because no shader formats are supported. Defaulting to source shader program compilation.')
            else:
                _logger.error('Cannot find shader binary file "%s". Defaulting to source shader program compilation.', binary_filepath)

        shader = cls()
        for _type, filepath in stages.items():
            shader.add_stage(_type, filepath)

        return shader

    def __init__(self, binary_filepath: str | None = None, save_binary: bool = True):
        super().__init__()

        self._binary_filepath = binary_filepath
        self._binary_load = _load_thread_executor.submit(_read_binary, binary_filepath) if binary_filepath else None
        self._source_loads: dict[ShaderType, futures.Future[str]] = {}
        self._uniforms: dict[str, int] = {}
        self._attributes: dict[str, int] = {}
        self._save_binary = save_binary and not binary_filepath

    @debug.profiled('graphics', 'shaders', 'initialization')
    def initialize(self) -> None:
        super().initialize()

        self._id = GL.GLuint(GL.glCreateProgram())

        if self._binary_load is not None:
            self._load_from_binary()
        else:
            self._load_from_sources()

        self._check_link_status()
        self._retrieve_interface()

        _logger.info('Shader program %d compiled succesfully.', self.id)

        if self._save_binary:
            if not _binary_formats_supported():
                _logger.error('Cannot save shader binary because no binary formats are supported.')
                return

            fut = _load_thread_executor.submit(_save_binary, t.cast(str, self._binary_filepath), *self._retrieve_binary())
            fut.add_done_callback(lambda _: _logger.info('Binary of shader program %d saved as "%s".', self.id, self._binary_filepath))

    @debug.profiled('graphics', 'cleanup')
    def delete(self) -> None:
        super().delete()

        GL.glDeleteProgram(self.id)

    @debug.profiled('graphics', 'shaders', 'initialization')
    def add_stage(self, _type: ShaderType, filepath: str) -> None:
        if self.is_initialized:
            _logger.error('Cannot add stage to alread linked shader program %d.', self.id)
            return

        if _type in self._source_loads:
            _logger.warning('Shader of type %s has been already requested to be loaded into program %d.', _type, self.id)
            return

        self._source_loads[_type] = _load_thread_executor.submit(_read_source, filepath)

    @debug.profiled('graphics', 'shaders')
    def validate(self) -> None:
        '''
        Validates shader against current OpenGL state.
        '''

        self.ensure_initialized()
        GL.glValidateProgram(self.id)

        if (info_log := GL.glGetProgramInfoLog(self.id)) != '':
            raise SpykeException(f'Shader program {self.id} validation failure:\n{info_log}')

        _logger.debug('Shader program %d has been validated succesfully.', self.id)

    @debug.profiled('graphics', 'shaders', 'rendering')
    def use(self) -> None:
        self.ensure_initialized()
        GL.glUseProgram(self.id)

    def get_attrib_location(self, name: str) -> int:
        self.ensure_initialized()

        assert name in self._attributes, f'Cannot find attribute "{name}" of program {self.id}.'
        return self._attributes[name]

    def get_uniform_location(self, name: str) -> int:
        self.ensure_initialized()

        assert name in self._uniforms, f'Cannot find uniform "{name}" of program {self.id}.'
        return self._uniforms[name]

    @functools.cache
    def get_uniform_block_location(self, name: str) -> int:
        self.ensure_initialized()
        loc = GL.glGetUniformBlockIndex(self.id, name)
        assert loc != -1, f'Cannot find uniform block named "{name}".'

        return loc

    def set_uniform_block_binding(self, name: str, index: int) -> None:
        self.ensure_initialized()
        loc = self.get_uniform_block_location(name)
        GL.glUniformBlockBinding(self.id, loc, index)

    @t.overload
    def set_uniform(self, name: str, value: int) -> None: ...

    @t.overload
    def set_uniform(self, name: str, value: float) -> None: ...

    @debug.profiled('graphics', 'shaders', 'rendering')
    def set_uniform(self, name: str, value: int | float) -> None:
        self.ensure_initialized()
        loc = self.get_uniform_location(name)

        if isinstance(value, int):
            GL.glProgramUniform1i(self.id, loc, value)
        elif isinstance(value, float):
            GL.glProgramUniform1f(self.id, loc, value)
        else:
            raise TypeError(f'Invalid type of uniform value: {type(value).__name__}')

    @t.overload
    def set_uniform_array(self, name: str, value: list[int]) -> None: ...

    @t.overload
    def set_uniform_array(self, name: str, value: list[float]) -> None: ...

    @t.overload
    def set_uniform_array(self, name: str, value: npt.NDArray[np.float32]) -> None: ...

    @t.overload
    def set_uniform_array(self, name: str, value: npt.NDArray[np.int32]) -> None: ...

    @t.overload
    def set_uniform_array(self, name: str, value: npt.NDArray[np.uint32]) -> None: ...

    @debug.profiled('graphics', 'shaders', 'rendering')
    def set_uniform_array(self, name: str, value: list[int] | list[float] | npt.NDArray[np.int32] | npt.NDArray[np.float32] | npt.NDArray[np.uint32]) -> None:
        self.ensure_initialized()
        loc = self.get_uniform_location(name)

        _len = len(value)
        if _len == 0:
            return

        if isinstance(value, np.ndarray):
            if value.dtype == np.int32:
                GL.glProgramUniform1iv(self.id, loc, _len, value)
            elif value.dtype == np.uint32:
                GL.glProgramUniform1uiv(self.id, loc, _len, value)
            elif value.dtype == np.float32:
                GL.glProgramUniform1fv(self.id, loc, _len, value)
            else:
                raise TypeError(f'Invalid dtype for np.ndarray: {value.dtype}')
        elif isinstance(value[0], int):
            GL.glProgramUniform1iv(self.id, loc, _len, np.asarray(value, dtype=np.int32))
        elif isinstance(value[0], float):
            GL.glProgramUniform1fv(self.id, loc, _len, np.asarray(value, dtype=np.float32))
        else:
            raise TypeError(f'Invalid type of uniform value: {type(value).__name__}')

    @t.overload
    def set_uniform_matrix(self, name: str, value: glm.mat2, transpose: bool) -> None: ...

    @t.overload
    def set_uniform_matrix(self, name: str, value: glm.mat3, transpose: bool) -> None: ...

    @t.overload
    def set_uniform_matrix(self, name: str, value: glm.mat4, transpose: bool) -> None: ...

    @debug.profiled('graphics', 'shaders', 'rendering')
    def set_uniform_matrix(self, name: str, value: glm.mat2 | glm.mat3 | glm.mat4, transpose: bool) -> None:
        # TODO: Add support for matrices which width and height differ
        self.ensure_initialized()
        loc = self.get_uniform_location(name)

        _len = value.length()
        if _len == 2:
            GL.glProgramUniformMatrix2fv(self.id, loc, 1, transpose, glm.value_ptr(value))
        elif _len == 3:
            GL.glProgramUniformMatrix3fv(self.id, loc, 1, transpose, glm.value_ptr(value))
        elif _len == 4:
            GL.glProgramUniformMatrix4fv(self.id, loc, 1, transpose, glm.value_ptr(value))
        else:
            raise SpykeException(f'Invalid uniform matrix size {_len}x{_len}.')

    # TODO: Probably convert those two dicts to be immutable
    @property
    def uniforms(self) -> dict[str, int]:
        return self._uniforms

    @property
    def attributes(self) -> dict[str, int]:
        return self._attributes

    def _check_link_status(self):
        if (info_log := GL.glGetProgramInfoLog(self.id)) != '':
            raise SpykeException(f'Shader program {self.id} link failure:\n{info_log}.')

    def _retrieve_interface(self) -> None:
        # via: https://stackoverflow.com/a/50382656

        uniform_count = GL.glGetProgramiv(self.id, GL.GL_ACTIVE_UNIFORMS)
        for i in range(uniform_count):
            name, _, _ = GL.glGetActiveUniform(self.id, i)
            name = name.decode(_ENCODING)
            if name.endswith(']'):
                name = name[:-3]

            loc = GL.glGetUniformLocation(self.id, name)
            if loc == -1:
                # we ignore everything located in uniform blocks
                continue
            self._uniforms[name] = loc

        attrib_count = GL.glGetProgramiv(self.id, GL.GL_ACTIVE_ATTRIBUTES)
        for i in range(attrib_count):
            name, _, _ = GL.glGetActiveAttrib(self.id, i)
            name = name.decode(_ENCODING)
            if name.endswith(']'):
                name = name[:-3]

            loc = GL.glGetAttribLocation(self.id, name)
            self._attributes[name] = loc

    def _load_from_binary(self) -> None:
        self._binary_load = t.cast(futures.Future[tuple[int, bytes]], self._binary_load)

        if not _binary_formats_supported():
            raise SpykeException('Driver doesn\'t support any binary formats.')

        _logger.info('Loading shader program %d from binary.', self.id)

        if (exc := self._binary_load.exception()) is not None:
            raise SpykeException(f'Binary of shader program {self.id} loading error: {exc}.') from exc

        _format, binary = self._binary_load.result()
        GL.glShaderBinary(self.id, _format, binary, len(binary))

    def _load_from_sources(self) -> None:
        shaders: list[int] = []
        for _type, fut in self._source_loads.items():
            if (exc := fut.exception()) is not None:
                raise SpykeException(f'{_type.name} shader of program {self.id} loading error: {exc}.') from exc

            shader = _create_shader(_type, fut.result())
            GL.glAttachShader(self.id, shader)
            shaders.append(shader)

        GL.glLinkProgram(self.id)

        for shader in shaders:
            GL.glDetachShader(self.id, shader)
            GL.glDeleteShader(shader)

    def _retrieve_binary(self) -> tuple[int, bytes]:
        length = GL.glGetProgramiv(self.id, GL.GL_PROGRAM_BINARY_LENGTH)
        _format = GL.GLint()
        binary = GL.glGetProgramBinary(self.id, length, None, _format)

        return (_format, binary)

@debug.profiled('graphics', 'shaders', 'initialization', 'io')
def _read_source(filepath: str) -> str:
    if not os.path.exists(filepath):
        raise SpykeException(f'Shader file {filepath} not found.')

    with open(filepath, 'r') as f:
        return f.read()

@debug.profiled('graphics', 'shaders', 'initialization', 'io')
def _read_binary(filepath: str) -> tuple[int, bytes]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'Shader binary file "{filepath}" not found.')

    base = os.path.splitext(os.path.basename(filepath))[0]
    components = base.split('_')
    if len(components) < 2:
        raise SpykeException('Binary shader filename should end with _{format} (i.e. "basic_2137.bin").')

    if not components[1].isdigit():
        raise SpykeException(f'Format name in "{filepath}" is not a number.')

    _format = int(components[1])
    with open(filepath, 'rb') as f:
        binary = f.read()

    return (_format, binary)

def _binary_formats_supported() -> bool:
    return bool(GL.glGetInteger(GL.GL_NUM_SHADER_BINARY_FORMATS))

def _save_binary(filepath: str, _format: int, binary: bytes) -> None:
    with open(filepath, 'wb+') as f:
        f.write(binary)

def _create_shader(_type: ShaderType, source: str) -> int:
    shader = GL.glCreateShader(_type)

    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)

    if (info_log := GL.glGetShaderInfoLog(shader)) != '':
        raise SpykeException(f'{_type.name} {shader} compilation failure:\n{info_log}.')

    return shader

_logger = logging.getLogger(__name__)
_load_thread_executor = futures.ThreadPoolExecutor(thread_name_prefix='ShaderLoad')
