from . import shaderSources
from ..enums import ShaderType
from ..utils import ObjectManager
from ..debug import Log, LogLevel
from ...transform import Matrix4

from OpenGL import GL
import numpy
from functools import lru_cache

class Shader(object):
	@staticmethod
	def __CompileShader(source: str, type: ShaderType) -> int:
		shader = GL.glCreateShader(type)

		GL.glShaderSource(shader, source)
		GL.glCompileShader(shader)
		
		infoLog = GL.glGetShaderInfoLog(shader)
		if len(infoLog) != 0:
			GL.glDeleteShader(shader)
			raise RuntimeError(f"Shader compilation error: {infoLog}.")

		return shader

	@classmethod
	def FromFile(cls, vertFile: str, fragFile: str):
		try:
			with open(vertFile, "r") as f:
				vertSource = f.read()
			with open(fragFile, "r") as f:
				fragSource = f.read()
		except FileNotFoundError as e:
			raise RuntimeError(f"Cannot find shader file named '{e.filename}'")

		return cls(vertSource, fragSource)
	
	def __init__(self, vertSource: str, fragSource: str):
		vertShader = Shader.__CompileShader(vertSource, GL.GL_VERTEX_SHADER)
		fragShader = Shader.__CompileShader(fragSource, GL.GL_FRAGMENT_SHADER)

		self.__id = GL.glCreateProgram()
		GL.glAttachShader(self.__id, vertShader)
		GL.glAttachShader(self.__id, fragShader)
		
		GL.glLinkProgram(self.__id)
		GL.glValidateProgram(self.__id)

		GL.glDetachShader(self.__id, vertShader)
		GL.glDetachShader(self.__id, fragShader)

		GL.glDeleteShader(vertShader)
		GL.glDeleteShader(fragShader)

		infoLog = GL.glGetProgramInfoLog(self.__id)
		if len(infoLog) != 0:
			raise RuntimeError(f"Shader program compilation error: {infoLog}.")

		self.uniforms = {}

		ObjectManager.AddObject(self)
	
	def Use(self) -> None:
		GL.glUseProgram(self.__id)
	
	def Delete(self) -> None:
		GL.glDeleteProgram(self.__id)

	@lru_cache
	def GetAttribLocation(self, name: str) -> int:
		loc = GL.glGetAttribLocation(self.__id, name)
		if loc == -1:
			Log(f"Cannot find attribute named '{name}'", LogLevel.Warning)

		return loc
	
	@lru_cache
	def GetUniformLocation(self, name: str) -> int:
		if name in self.uniforms.keys():
			return self.uniforms[name]

		loc = GL.glGetUniformLocation(self.__id, name)

		if loc == -1:
			Log(f"cannot find uniform named '{name}'", LogLevel.Warning)
		else:
			self.uniforms[name] = loc
		
		return loc
	
	def SetUniform1i(self, name: str, value: int) -> None:
		GL.glUniform1i(self.GetUniformLocation(name), value)

	def SetUniform1f(self, name: str, value: float) -> None:
		GL.glUniform1f(self.GetUniformLocation(name), value)
	
	def SetUniformMat4(self, name: str, value: Matrix4, transpose: bool) -> None:
		GL.glUniformMatrix4fv(self.GetUniformLocation(name), 1, transpose, numpy.asarray(value, dtype="float32"))
	
	@property
	def ID(self) -> int:
		return self.__id