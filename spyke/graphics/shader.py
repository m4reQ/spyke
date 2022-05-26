import dataclasses
import logging
import typing as t
import functools
from os import path

import numpy as np
import glm
from OpenGL import GL

from spyke.enums import ShaderType
from spyke.exceptions import GraphicsException, SpykeException
from spyke.graphics import gl

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
    def __init__(self, shader_spec: ShaderSpec, auto_compile: bool=True):
        super().__init__()

        self._id: int = 0
        self._stages: t.List[int] = []
        self._uniforms: t.Dict[str, int] = {}
        self._is_compiled = False
        self._spec = shader_spec
        
        if auto_compile:
            self.compile()

    def compile(self) -> None:
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

    def validate(self) -> None:
        if not self._is_compiled:
            _logger.error('Cannot validate not compiled shader program.')
            return

        GL.glValidateProgram(self.id)

        info_log = GL.glGetProgramInfoLog(self.id)
        if info_log != '':
            raise SpykeException(f'Shader program {self.id} validation failure:\n{info_log}')

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

    @functools.lru_cache
    def get_uniform_location(self, name: str) -> int:
        if name in self._uniforms:
            return self._uniforms[name]

        loc = GL.glGetUniformLocation(self.id, name)
        assert loc != -1, f'Cannot find uniform named "{name}".'

        self._uniforms[name] = loc

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
