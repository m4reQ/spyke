from ...utils import Serializable

import glm

class TransformComponent(Serializable):
	ClassName = "TransformComponent"

	@classmethod
	def Deserialize(cls, data: str):
		data = data.split(" ")

		data = [float(x) for x in data]

		pos = glm.vec3(data[0], data[1], data[2])
		size = glm.vec3(data[3], data[4], data[5])
		rot = glm.vec3(data[6], data[7], data[8])

		return cls(pos, size, rot)

	def __init__(self, pos: glm.vec3, size: glm.vec3, rotation: glm.vec3):
		self.__pos = pos
		self.__size = size

		_rotation = glm.mod(rotation, 360.0)
		self.__rot = glm.radians(_rotation)
		self.__rotHint = rotation

		self.__posChanged = True
		self.__sizeChanged = True
		self.__rotChanged = True

		self.Matrix = glm.mat4(1.0)
		
		self.Recalculate()

		self.__transMatrix = glm.mat4(1.0)
		self.__scaleMatrix = glm.mat4(1.0)
		self.__rotQuat = glm.quat(self.__rot)

	def Recalculate(self):
		if self.__posChanged:
			self.__transMatrix = glm.translate(glm.mat4(1.0), self.__pos)
			self.__posChanged = False
		
		if self.__rotChanged:
			self.__rotQuat = glm.quat(glm.radians(self.__rot))
			self.__rotChanged = False
		
		if self.__sizeChanged:
			self.__scaleMatrix = glm.scale(glm.mat4(1.0), self.__size)
			self.__sizeChanged = False
		
		self.Matrix = self.__transMatrix * glm.mat4_cast(self.__rotQuat) * self.__scaleMatrix

	def Serialize(self):
		s = f"{self.__pos.x} {self.__pos.y} {self.__pos.z} "
		s += f"{self.__size.x} {self.__size.y} {self.__size.z} "
		s += f"{self.__rot.x} {self.__rot.y} {self.__rot.z}"

		return s

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
	def Size(self, val: glm.vec3):
		self.__size = val
		self.__sizeChanged = True
	
	@property
	def Rotation(self):
		return self.__rot
	
	@Rotation.setter
	def Rotation(self, val: glm.vec3):
		self.__rot = glm.mod(val, 360.0)
		self.__rotHint = val

		self.__rotChanged = True

	@property
	def RotationRadians(self):
		return glm.radians(self.__rot)
	
	@property
	def RotationUser(self):
		return self.__rotHint