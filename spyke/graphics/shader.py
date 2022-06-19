import dataclasses
import logging
import typing as t
import functools
from os import path

import numpy as np
import numpy.typing as npt
import glm
from OpenGL import GL

from spyke.enums import ShaderType
from spyke.exceptions import SpykeException
from spyke.graphics import gl
from spyke import debug

_logger = logging.getLogger(__name__)

@dataclasses.dataclass
class ShaderSpec:
    vertex_filepath: str
    fragment_filepath: str
    geometry_filepath: t.Optional[str] = None
    compute_filepath: t.Optional[str] = None
    tess_eval_filepath: t.Optional[str] = None
    tess_control_filepath: t.Optional[str] = None

class Shader(gl.GLObject):
    @debug.profiled('graphics', 'shaders')
    def __init__(self, shader_spec: ShaderSpec, auto_compile: bool=True):
        super().__init__()

        self._id: int = 0
        self._stages: list[int] = []
        self._is_compiled = False
        self._spec = shader_spec

        if auto_compile:
            self.compile()

    @debug.profiled('graphics', 'shaders')
    def compile(self) -> None:
        '''
        Compiles all shaders and links program from given
        shader specification.
        '''
        
        if self._is_compiled:
            _logger.warning('Shader program is already compiled.')
            return

        self._id = gl.create_program()
        assert self._id != 0, 'Could not create shader program'

        self._create_stage_and_attach(self._spec.vertex_filepath, ShaderType.VertexShader)
        self._create_stage_and_attach(self._spec.fragment_filepath, ShaderType.FragmentShader)

        if self._spec.geometry_filepath is not None:
            self._create_stage_and_attach(self._spec.geometry_filepath, ShaderType.GeometryShader)

        if self._spec.compute_filepath is not None:
            self._create_stage_and_attach(self._spec.compute_filepath, ShaderType.ComputeShader)

        if self._spec.tess_eval_filepath is not None:
            self._create_stage_and_attach(self._spec.tess_eval_filepath, ShaderType.TessEvaluationShader)

        if self._spec.tess_control_filepath is not None:
            self._create_stage_and_attach(self._spec.tess_control_filepath, ShaderType.TessControlShader)

        GL.glLinkProgram(self.id)
        info_log = GL.glGetProgramInfoLog(self.id)
        if info_log != '':
            raise SpykeException(f'Shader program {self.id} link failure:\n{info_log}')

        self._cleanup_stages()
        self._is_compiled = True

        _logger.info('Shader program %d compiled succesfully.', self.id)

    @debug.profiled('graphics', 'shaders')
    def validate(self) -> None:
        '''
        Validates shader against current OpenGL state.
        '''
        
        if not self._is_compiled:
            _logger.error('Cannot validate not compiled shader program.')
            return

        GL.glValidateProgram(self.id)

        info_log = GL.glGetProgramInfoLog(self.id)
        if info_log != '':
            raise SpykeException(f'Shader program {self.id} validation failure:\n{info_log}')

        _logger.debug('%s has been validated succesfully.', self)

    @debug.profiled('graphics', 'shaders')
    def use(self) -> None:
        GL.glUseProgram(self.id)

    @functools.cache
    def get_attrib_location(self, name: str) -> int:
        loc = GL.glGetAttribLocation(self.id, name)
        assert loc != -1, f'Cannot find attribute named "{name}".'

        return loc

    @functools.cache
    def get_uniform_location(self, name: str) -> int:
        loc = GL.glGetUniformLocation(self.id, name)
        assert loc != -1, f'Cannot find uniform named "{name}".'

        return loc

    @functools.cache
    def get_uniform_block_location(self, name: str) -> int:
        loc = GL.glGetUniformBlockIndex(self.id, name)
        assert loc != -1, f'Cannot find uniform block named "{name}".'

        return loc

    def set_uniform_block_binding(self, name: str, index: int) -> None:
        loc = self.get_uniform_block_location(name)
        GL.glUniformBlockBinding(self.id, loc, index)

    @t.overload
    def set_uniform(self, name: str, value: int) -> None: ...
    
    @t.overload
    def set_uniform(self, name: str, value: float) -> None: ...
    
    def set_uniform(self, name: str, value: t.Union[int, float]) -> None:
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
    
    def set_uniform_array(self, name: str, value: t.Union[list[int], list[float], npt.NDArray[np.int32], npt.NDArray[np.float32], npt.NDArray[np.uint32]]) -> None:
        loc = self.get_uniform_location(name)
        
        _len = len(value)
        if _len == 0:
            return
        
        # only check the first element for performance
        if isinstance(value[0], int):
            GL.glProgramUniform1iv(self.id, loc, _len, np.asarray(value, dtype=np.int32))
        elif isinstance(value[0], float):
            GL.glProgramUniform1fv(self.id, loc, _len, np.asarray(value, dtype=np.float32))
        elif isinstance(value, np.ndarray):
            if value.dtype == np.int32:
                GL.glProgramUniform1iv(self.id, _len, value)
            if value.dtype == np.uint32:
                GL.glProgramUniform1uiv(self.id, _len, value)
            if value.dtype == np.float32:
                GL.glProgramUniform1fv(self.id, _len, value)
        else:
            raise TypeError(f'Invalid type of uniform value: {type(value).__name__}')
    
    @t.overload
    def set_uniform_matrix(self, name: str, value: glm.mat2, transpose: bool) -> None: ...
    
    @t.overload
    def set_uniform_matrix(self, name: str, value: glm.mat3, transpose: bool) -> None: ...
    
    @t.overload
    def set_uniform_matrix(self, name: str, value: glm.mat4, transpose: bool) -> None: ...
    
    # TODO: Add support for matrices which width and height differ
    def set_uniform_matrix(self, name: str, value: t.Union[glm.mat2, glm.mat3, glm.mat4], transpose: bool) -> None:
        loc = self.get_uniform_location(name)
        
        if value.length() == 2:
            GL.glProgramUniformMatrix2fv(self.id, loc, 1, transpose, glm.value_ptr(value))
        elif value.length() == 3:
            GL.glProgramUniformMatrix3fv(self.id, loc, 1, transpose, glm.value_ptr(value))
        elif value.length() == 4:
            GL.glProgramUniformMatrix4fv(self.id, loc, 1, transpose, glm.value_ptr(value))

    def _cleanup_stages(self) -> None:
        for shader in self._stages:
            GL.glDetachShader(self.id, shader)
            GL.glDeleteShader(shader)

        self._stages.clear()

    def _create_stage_and_attach(self, filepath: str, _type: ShaderType) -> None:
        if self._is_compiled:
            _logger.error('Cannot attach shader to already compiled program.')
            return

        if not path.exists(filepath):
            raise SpykeException(f'Shader file {filepath} not found.')

        with open(filepath, 'r') as f:
            source = f.read()

        shader = GL.glCreateShader(_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        info_log = GL.glGetShaderInfoLog(shader)
        if info_log != '':
            raise SpykeException(f'Shader {shader} of type {_type.name} compilation failure:\n{info_log}')

        GL.glAttachShader(self.id, shader)
        self._stages.append(shader)

    def _delete(self) -> None:
        GL.glDeleteProgram(self.id)
