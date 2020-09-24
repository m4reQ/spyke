from ...graphics.text.font import Font

import glm

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
		if self.__posChanged:
			self.__transMatrix = glm.translate(glm.mat4(1.0), self.__pos)
		
		if self.__rotChanged:
			self.__rotMatrix = glm.rotate(glm.mat4(1.0), self.__rot, glm.vec3(0.0, 0.0, 1.0))
		
		if self.__sizeChanged:
			self.__scaleMatrix = glm.scale(glm.mat4(1.0), glm.vec3(self.__size.x, self.__size.y, 0.0))
		
		self.Matrix = self.__transMatrix * self.__rotMatrix * self.__scaleMatrix
	
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
	def __init__(self, pos: glm.vec3, text: str, color: tuple, size: int, font: Font):
		self.Text = text
		self.Color = color
		self.Size = size
		self.Font = font