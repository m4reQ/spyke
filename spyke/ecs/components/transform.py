from ...autoslot import WeakSlots
import glm

class TransformComponent(WeakSlots):
	def __init__(self, pos: glm.vec3, size: glm.vec3, rotation: glm.vec3):
		self._pos = pos
		self._size = size
		self._rot = glm.mod(rotation, 360.0)
		self._rotHint = rotation

		self.__posChanged = True
		self.__sizeChanged = True
		self.__rotChanged = True

		self.matrix = glm.mat4(1.0)

		self._transMat = glm.mat4(1.0)
		self._scaleMat = glm.mat4(1.0)
		self._rotQuat = glm.quat(self._rot)
		
		self.RecalculateMatrices()

	def RecalculateMatrices(self):
		if self.__posChanged:
			self._transMat = glm.translate(glm.mat4(1.0), self._pos)
			self.__posChanged = False
		
		if self.__rotChanged:
			self._rotQuat = glm.quat(glm.radians(self._rot))
			self.__rotChanged = False
		
		if self.__sizeChanged:
			self._scaleMat = glm.scale(glm.mat4(1.0), self._size)
			self.__sizeChanged = False
		
		self.matrix = self._transMat * glm.mat4_cast(self._rotQuat) * self._scaleMat

	@property
	def shouldRecalculate(self):
		return any([self.__posChanged, self.__sizeChanged, self.__rotChanged])

	@property
	def position(self):
		return self._pos
	
	@position.setter
	def position(self, val: glm.vec3):
		self._pos = val
		self.__posChanged = True
	
	@property
	def size(self):
		return self._size
	
	@size.setter
	def size(self, val: glm.vec3):
		self._size = val
		self.__sizeChanged = True
	
	@property
	def rotation(self):
		return self._rot
	
	@rotation.setter
	def rotation(self, val: glm.vec3):
		self._rot = glm.mod(val, 360.0)
		self._rotHint = val
		self.__rotChanged = True