from ..transform import CreateTransform
from ..graphics import Font, TextureHandle
from ..debug import Log, LogLevel

import glm

class ColorComponent(object):
	def __init__(self, *args):
		if isinstance(args[0], tuple):
			tup = args[0]
			self.R = tup[0]
			self.G = tup[1]
			self.B = tup[2]
			self.A = tup[3]
		elif len(args) == 4:
			self.R = args[0]
			self.G = args[1]
			self.B = args[2]
			self.A = args[3]
		else:
			raise TypeError("Invalid color arguments.")
	
	def __iter__(self):
		yield self.R
		yield self.G
		yield self.B
		yield self.A

class TransformComponent(object):
	def __init__(self, pos: glm.vec3, size: glm.vec2, rotation: float):
		self.__pos = pos
		self.__size = size
		self.__rot = rotation

		self.__posChanged = True
		self.__sizeChanged = True
		self.__rotChanged = True

		self.Matrix = glm.mat4(1.0)
		
		self.Recalculate()

		self.__transMatrix = glm.mat4(1.0)
		self.__rotMatrix = glm.mat4(1.0)
		self.__scaleMatrix = glm.mat4(1.0)
	
	def Recalculate(self):
		if all([self.__posChanged, self.__rotChanged, self.__sizeChanged]):
			self.Matrix = CreateTransform(self.__pos, self.__size, self.__rot)
			return
			
		if self.__posChanged:
			self.__transMatrix = glm.translate(glm.mat4(1.0), self.__pos)
		
		if self.__rotChanged:
			self.__rotMatrix = glm.rotate(glm.mat4(1.0), self.__rot, glm.vec3(0.0, 0.0, 1.0))
		
		if self.__sizeChanged:
			self.__scaleMatrix = glm.scale(glm.mat4(1.0), glm.vec3(self.__size.x, self.__size.y, 0.0))
		
		self.Matrix = self.__transMatrix * self.__rotMatrix * self.__scaleMatrix

		Log("Recalculate", LogLevel.Info)
	
	@property
	def ShouldRecalculate(self):
		return any([self.__posChanged, self.__sizeChanged, self.__rotChanged])

	@property
	def Position(self):
		return self.__pos
	
	@Position.setter
	def Position(self, val: glm.vec3):
		self.__pos = val
		self.__posChanged = True
	
	@property
	def Size(self):
		return self.__size
	
	@Size.setter
	def Size(self, val: glm.vec2):
		self.__size = val
		self.__sizeChanged = True
	
	@property
	def Rotation(self):
		return self.__rot
	
	@Rotation.setter
	def Rotation(self, val: float):
		self.__rot = val
		self.__rotChanged = True

class TextComponent(object):
	def __init__(self, text: str, size: int, font: Font):
		self.Text = text
		self.Size = size
		self.Font = font

class SpriteComponent(object):
	def __init__(self, textureHandle: TextureHandle, tilingFactor: tuple):
		self.TextureHandle = textureHandle
		self.TilingFactor = tilingFactor