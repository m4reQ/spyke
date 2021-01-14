#region Import
from ..enums import ShaderType
from ..debug import Log, LogLevel, GetGLError
from ..managers.objectManager import ObjectManager
from ..utils import EnsureString
from ..transform import Matrix4

from OpenGL import GL
import numpy
from functools import lru_cache
#endregion

class Shader(object):
	def __init__(self):
		self.__id = GL.glCreateProgram()

		self.uniforms = {}
		self.__stages = []

		self.__compiled = False

		ObjectManager.AddObject(self)
	
	def AddStage(self, stage: ShaderType, filepath: str) -> None:
		if self.__compiled:
			Log("Tried to add shader stage to already compiled shader.", LogLevel.Warning)
			return

		try:
			with open(filepath, "r") as f:
				source = f.read()
		except FileNotFoundError as e:
			raise RuntimeError(f"Cannot find shader file named '{e.filename}'")

		shader = GL.glCreateShader(stage)
		self.__stages.append(shader)

		GL.glShaderSource(shader, source)
		GL.glCompileShader(shader)
		
		infoLog = GL.glGetShaderInfoLog(shader)
		if len(infoLog) != 0:
			GL.glDeleteShader(shader)
			raise RuntimeError(f"Shader (file: '{filepath}') compilation error:\n{EnsureString(infoLog)}.")

		GL.glAttachShader(self.__id, shader)
	
	def Compile(self) -> None:
		if self.__compiled:
			LogLevel("Shader already compiled.", LogLevel.Warning)
			return

		GL.glLinkProgram(self.__id)
		GL.glValidateProgram(self.__id)

		for stage in self.__stages:
			GL.glDetachShader(self.__id, stage)
			GL.glDeleteShader(stage)

		infoLog = GL.glGetProgramInfoLog(self.__id)
		if len(infoLog) != 0:
			raise RuntimeError(f"Shader program (id: {self.__id}) compilation error:\n{EnsureString(infoLog)}.")
		else:
			Log(f"Shader program (id: {self.__id}) compiled succesfully.", LogLevel.Info)

		self.__stages.clear()
		self.__compiled = True
	
	def Use(self) -> None:
		GL.glUseProgram(self.__id)

	def Delete(self) -> None:
		GL.glDeleteProgram(self.__id)

	@lru_cache
	def GetAttribLocation(self, name: str) -> int:
		loc = GL.glGetAttribLocation(self.__id, name)
		if loc == -1:
			Log(f"Cannot find attribute named '{name}'.", LogLevel.Warning)

		return loc
	
	@lru_cache
	def GetUniformLocation(self, name: str) -> int:
		if name in self.uniforms.keys():
			return self.uniforms[name]

		loc = GL.glGetUniformLocation(self.__id, name)

		if loc == -1:
			Log(f"cannot find uniform named '{name}'.", LogLevel.Warning)
		else:
			self.uniforms[name] = loc
			self.GetUniformLocation.cache_clear()
		
		return loc
	
	def GetUniformBlockLocation(self, name: str) -> int:
		loc = GL.glGetUniformBlockIndex(self.__id, name)
		
		if loc == -1:
			Log(f"Cannot find uniform block named '{name}'.", LogLevel.Warning)
		
		return loc
	
	def SetUniformBlockBinding(self, name: str, index: int) -> None:
		loc = self.GetUniformBlockLocation(name)
		GL.glUniformBlockBinding(self.__id, loc, index)
	
	#region Setters
	def SetUniformIntArray(self, name: str, values: list) -> None:
		GL.glUniform1iv(self.GetUniformLocation(name), len(values), numpy.asarray(values, dtype = numpy.int32))

	def SetUniform1i(self, name: str, value: int) -> None:
		GL.glUniform1i(self.GetUniformLocation(name), value)

	def SetUniform1f(self, name: str, value: float) -> None:
		GL.glUniform1f(self.GetUniformLocation(name), value)
	
	def SetUniformMat4(self, name: str, value: Matrix4, transpose: bool) -> None:
		GL.glUniformMatrix4fv(self.GetUniformLocation(name), 1, transpose, numpy.asarray(value, dtype="float32"))
	#endregion
	
	@property
	def ID(self) -> int:
		return self.__id