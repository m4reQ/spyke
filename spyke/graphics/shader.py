#region Import
from spyke.graphics import gl
from spyke import debug
from ..utils import EnsureString
from ..exceptions import GraphicsException, SpykeException
from ..constants import _NP_INT, _NP_FLOAT

from OpenGL import GL
import numpy as np
import glm
from functools import lru_cache
#endregion

class Shader(gl.GLObject):
	def __init__(self):
		super().__init__()

		self._id = gl.create_program()

		self.uniforms = {}
		self.__stages = []

		self.__compiled = False
	
	def AddStage(self, stage: int, filepath: str) -> None:
		if self.__compiled:
			debug.log_warning('Tried to add shader stage to already compiled shader.')
			return

		try:
			with open(filepath, "r") as f:
				source = f.read()
		except FileNotFoundError as e:
			raise SpykeException(f"Cannot find shader file named '{e.filename}'")

		shader = GL.glCreateShader(stage)
		self.__stages.append(shader)

		GL.glShaderSource(shader, source)
		GL.glCompileShader(shader)
		
		infoLog = GL.glGetShaderInfoLog(shader)
		if len(infoLog) != 0:
			raise GraphicsException(f'{self} compilation error:\n{infoLog.decode("ansi")}.')

		GL.glAttachShader(self.id, shader)
	
	def Compile(self) -> None:
		if self.__compiled:
			debug.log_warning('Shader already compiled.')
			return

		GL.glLinkProgram(self.id)

		for stage in self.__stages:
			GL.glDetachShader(self.id, stage)
			GL.glDeleteShader(stage)

		self.__stages.clear()
		self.__compiled = True

		debug.log_info(f'{self} compiled succesfully.')
	
	def Validate(self) -> None:
		if not self.__compiled:
			debug.log_warning('Cannot validate not compiled shader program.')
			return
		
		GL.glValidateProgram(self.id)

		info_log = GL.glGetProgramInfoLog(self.id)
		if len(info_log) != 0:
			raise GraphicsException(f'{self} validation failure:\n{info_log.decode("ansi")}.')
		
		debug.log_info(f'{self} has been validated succesfully.')
	
	def Use(self) -> None:
		GL.glUseProgram(self.id)

	def delete(self) -> None:
		GL.glDeleteProgram(self.id)

	@lru_cache
	def GetAttribLocation(self, name: str) -> int:
		loc = GL.glGetAttribLocation(self.id, name)
		if loc == -1:
			raise GraphicsException(f'Cannot find attribute named "{name}".')

		return loc

	def GetUniformLocation(self, name: str) -> int:
		if name in self.uniforms:
			return self.uniforms[name]

		loc = GL.glGetUniformLocation(self.id, name)
		if loc == -1:
			raise GraphicsException(f'Cannot find uniform named "{name}".')

		self.uniforms[name] = loc
		
		return loc
	
	@lru_cache
	def GetUniformBlockLocation(self, name: str) -> int:
		loc = GL.glGetUniformBlockIndex(self.id, name)
		if loc == -1:
			raise GraphicsException(f'Cannot find uniform block named "{name}".')
		
		return loc
	
	def SetUniformBlockBinding(self, name: str, index: int) -> None:
		loc = self.GetUniformBlockLocation(name)
		GL.glUniformBlockBinding(self.id, loc, index)
	
	def SetUniformIntArray(self, name: str, values: list) -> None:
		GL.glProgramUniform1iv(self.id, self.GetUniformLocation(name), len(values), np.asarray(values, dtype=np.int32))

	def SetUniform1i(self, name: str, value: int) -> None:
		GL.glProgramUniform1i(self.id, self.GetUniformLocation(name), value)

	def SetUniform1f(self, name: str, value: float) -> None:
		GL.glProgramUniform1f(self.id, self.GetUniformLocation(name), value)
	
	def SetUniformMat4(self, name: str, value: glm.mat4, transpose: bool) -> None:
		GL.glProgramUniformMatrix4fv(self.id, self.GetUniformLocation(name), 1, transpose, glm.value_ptr(value))