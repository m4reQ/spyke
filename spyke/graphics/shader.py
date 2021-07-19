#region Import
from .gl import GLObject
from ..debugging import Debug, LogLevel
from ..utils import EnsureString
from ..exceptions import GraphicsException, SpykeException
from ..constants import _NP_INT, _NP_FLOAT

from OpenGL import GL
import numpy as np
import glm
from functools import lru_cache
#endregion

class Shader(GLObject):
	def __init__(self):
		super().__init__()

		self._id = GL.glCreateProgram()

		self.uniforms = {}
		self.__stages = []

		self.__compiled = False
	
	def AddStage(self, stage: int, filepath: str) -> None:
		if self.__compiled:
			Debug.Log("Tried to add shader stage to already compiled shader.", LogLevel.Warning)
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
			raise GraphicsException(f"Shader (file: '{filepath}') compilation error:\n{EnsureString(infoLog)}.")

		GL.glAttachShader(self._id, shader)
	
	def Compile(self) -> None:
		if self.__compiled:
			LogLevel("Shader already compiled.", LogLevel.Warning)
			return

		GL.glLinkProgram(self._id)

		for stage in self.__stages:
			GL.glDetachShader(self._id, stage)
			GL.glDeleteShader(stage)

		self.__stages.clear()
		self.__compiled = True

		Debug.Log(f"Shader program (id: {self._id}) compiled succesfully.", LogLevel.Info)
	
	def Validate(self) -> None:
		if not self.__compiled:
			Debug.Log("Cannot validate not compiled shader program.", LogLevel.Warning)
			return
		
		GL.glValidateProgram(self._id)

		infoLog = GL.glGetProgramInfoLog(self._id)
		if len(infoLog) != 0:
			raise GraphicsException(f"Shader program (id: {self._id}) validation failure:\n{EnsureString(infoLog)}.")
		else:
			Debug.Log(f"Shader program (id: {self._id}) has been validated succesfully.", LogLevel.Info)
	
	def Use(self) -> None:
		GL.glUseProgram(self._id)

	def Delete(self, removeRef: bool) -> None:
		super().Delete(removeRef)
		GL.glDeleteProgram(self._id)

	@lru_cache
	def GetAttribLocation(self, name: str) -> int:
		loc = GL.glGetAttribLocation(self._id, name)
		if loc == -1:
			raise GraphicsException(f"Cannot find attribute named '{name}'.")

		return loc

	def GetUniformLocation(self, name: str) -> int:
		if name in self.uniforms:
			return self.uniforms[name]
		else:
			loc = GL.glGetUniformLocation(self._id, name)
			if loc == -1:
				raise GraphicsException(f"Cannot find uniform named '{name}'.")
			else:
				self.uniforms[name] = loc
			
			return loc
	
	@lru_cache
	def GetUniformBlockLocation(self, name: str) -> int:
		loc = GL.glGetUniformBlockIndex(self._id, name)
		if loc == -1:
			raise GraphicsException(f"Cannot find uniform block named '{name}'.")
		
		return loc
	
	def SetUniformBlockBinding(self, name: str, index: int) -> None:
		loc = self.GetUniformBlockLocation(name)
		GL.glUniformBlockBinding(self._id, loc, index)
	
	def SetUniformIntArray(self, name: str, values: list) -> None:
		GL.glProgramUniform1iv(self._id, self.GetUniformLocation(name), len(values), np.asarray(values, dtype=_NP_INT))

	def SetUniform1i(self, name: str, value: int) -> None:
		GL.glProgramUniform1i(self._id, self.GetUniformLocation(name), value)

	def SetUniform1f(self, name: str, value: float) -> None:
		GL.glProgramUniform1f(self._id, self.GetUniformLocation(name), value)
	
	def SetUniformMat4(self, name: str, value: glm.mat4, transpose: bool) -> None:
		GL.glProgramUniformMatrix4fv(self._id, self.GetUniformLocation(name), 1, transpose, glm.value_ptr(value))