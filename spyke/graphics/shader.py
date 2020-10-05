from ..utils import ObjectManager
from ..debug import Log, LogLevel
from . import shaderSources

from OpenGL import GL
from glm import mat4
import numpy

class Shader(object):
	@staticmethod
	def CompileShader(source, type):
		shader = GL.glCreateShader(type)

		GL.glShaderSource(shader, source)
		GL.glCompileShader(shader)
		
		infoLog = GL.glGetShaderInfoLog(shader)
		if len(infoLog) != 0:
			GL.glDeleteShader(shader)
			raise RuntimeError(f"Shader compilation error: {infoLog}.")

		return shader

	@classmethod
	def FromFile(cls, vertFile, fragFile):
		shader = None

		vertF = None
		fragF = None

		try:
			vertF = open(vertFile, "r")
			fragF = open(fragFile, "r")

			vertSource = vertF.read()
			fragSource = fragF.read()

			shader = cls(vertSource, fragSource)
		except FileNotFoundError as e:
			raise RuntimeError(f"Cannot find shader file named '{e.filename}'")
		finally:
			if vertF:
				vertF.close()
			if fragF:
				fragF.close()
		
		return shader
	
	@classmethod
	def Basic2D(cls):
		return cls(shaderSources.BASIC_VERTEX, shaderSources.BASIC_FRAGMENT)
	
	@classmethod
	def BasicText(cls):
		return cls(shaderSources.TEXT_VERTEX, shaderSources.TEXT_FRAGMENT)
	
	@classmethod
	def BasicLine(cls):
		return cls(shaderSources.LINE_VERTEX, shaderSources.LINE_FRAGMENT)
	
	@classmethod
	def BasicPostprocessing(cls):
		return cls(shaderSources.POST_VERTEX, shaderSources.POST_FRAGMENT)

	def __init__(self, vertSource, fragSource):
		vertShader = Shader.CompileShader(vertSource, GL.GL_VERTEX_SHADER)
		fragShader = Shader.CompileShader(fragSource, GL.GL_FRAGMENT_SHADER)

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
	
	def Use(self):
		GL.glUseProgram(self.__id)
	
	def Delete(self):
		GL.glDeleteProgram(self.__id)

	def GetAttribLocation(self, name):
		loc = GL.glGetAttribLocation(self.__id, name)
		if loc == -1:
			Log(f"Cannot find attribute named '{name}'", LogLevel.Warning)

		return loc
	
	def GetUniformLocation(self, name):
		if name in self.uniforms.keys():
			return self.uniforms[name]

		loc = GL.glGetUniformLocation(self.__id, name)

		if loc == -1:
			Log(f"cannot find uniform named '{name}'", LogLevel.Warning)
		else:
			self.uniforms[name] = loc
		
		return loc
	
	def SetUniform1i(self, name: str, value: int):
		loc = self.GetUniformLocation(name)

		GL.glUniform1i(loc, value)
	
	def SetUniformMat4(self, name: str, value: mat4, transpose: bool):
		loc = self.GetUniformLocation(name)

		GL.glUniformMatrix4fv(loc, 1, transpose, numpy.asarray(value, dtype="float32"))
	
	@property
	def ID(self):
		return self.__id