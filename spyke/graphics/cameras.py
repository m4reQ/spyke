from ..utils import Abstract

import glm

class Camera(Abstract):
	def Move(self, direction: glm.vec3, dt: float) -> None:
		pass
	
	def MoveTo(self, pos: glm.vec3) -> None:
		pass
	
	def ReinitProjectionMatrix(self, left: float, right: float, bottom: float, top: float, zNear: float = -1.0, zFar: float = 10.0) -> None:
		pass

	def RecalculateMatrices(self) -> None:
		pass

class OrthographicCamera(Camera):
	CameraSpeed = 13.0

	def __init__(self, left: float, right: float, bottom: float, top: float, zNear = -1.0, zFar = 10.0):
		self.projectionMatrix = glm.ortho(left, right, bottom, top, zNear, zFar)
		self.viewMatrix = glm.mat4(1.0)
		self.viewProjectionMatrix = glm.mat4(1.0)

		self.position = glm.vec2(0)

		self.left = left
		self.right = right
		self.bottom = bottom
		self.top = top
		self.zNear = zNear
		self.zFar = zFar

		self.RecalculateMatrices()
		self.shouldRecalculate = False
	
	def Move(self, direction: glm.vec2, dt: float):
		self.position += direction * dt * OrthographicCamera.CameraSpeed

		self.shouldRecalculate = True

	def MoveTo(self, pos: glm.vec2):
		self.position = pos

		self.shouldRecalculate = True
	
	def ReinitProjectionMatrix(self, left: float, right: float, bottom: float, top: float, zNear = -1.0, zFar = 10.0):
		self.projectionMatrix = glm.ortho(left, right, bottom, top, zNear, zFar)

		self.shouldRecalculate = True
		
	def RecalculateMatrices(self):
		transform = glm.translate(glm.mat4(1.0), glm.vec3(self.position.x, self.position.y, 0.0))

		self.viewMatrix = glm.inverse(transform)
		self.viewProjectionMatrix = self.projectionMatrix * self.viewMatrix
	