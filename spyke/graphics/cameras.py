import glm

_DEFAULT_CAMERA_SPEED = 15.0

class ACamera(object):
	def __init__(self):
		self.shouldRecalculate = False

		self.position = glm.vec3(0.0)
		self.speed = _DEFAULT_CAMERA_SPEED

		self.projectionMatrix = glm.mat4(1.0)
		self.viewMatrix = glm.mat4(1.0)
		self.viewProjectionMatrix = glm.mat4(1.0)
	
	def RecalculateMatrices(self) -> None:
		pass

class OrthographicCamera(ACamera):
	def __init__(self, left: float, right: float, bottom: float, top: float, zNear = -1.0, zFar = 10.0):
		super().__init__()
		self.left = left
		self.right = right
		self.bottom = bottom
		self.top = top
		self.zNear = zNear
		self.zFar = zFar

		self.projectionMatrix = glm.ortho(left, right, bottom, top, zNear, zFar)

		self.RecalculateMatrices()
	
	def Move(self, direction: glm.vec3, dt: float):
		self.position += direction * dt * self.speed
		self.shouldRecalculate = True

	def MoveTo(self, pos: glm.vec3):
		self.position = pos
		self.shouldRecalculate = True
	
	def ReinitProjectionMatrix(self, left: float, right: float, bottom: float, top: float, zNear = -1.0, zFar = 1.0):
		self.left = left
		self.right = right
		self.bottom = bottom
		self.top = top
		self.zNear = zNear
		self.zFar = zFar

		self.projectionMatrix = glm.ortho(left, right, bottom, top, zNear, zFar)
		self.shouldRecalculate = True
		
	def RecalculateMatrices(self):
		transform = glm.translate(glm.mat4(1.0), self.position)
		self.viewMatrix = glm.inverse(transform)
		self.viewProjectionMatrix = self.projectionMatrix * self.viewMatrix

		self.shouldRecalculate = False

class PerspectiveCamera(object):
	def __init__(self, fov, aspect, zNear = -1.0, zFar = 10.0):
		super().__init__()
		self.fov = fov
		self.aspect = aspect
		self.zNear = zNear
		self.zFar = zFar

		self.projectionMatrix = glm.perspective(fov, aspect, zNear, zFar)

		self.RecalculateMatrices()
	
	def Move(self, direction: glm.vec3, dt: float):
		self.position += direction * dt * self.speed
		self.shouldRecalculate = True

	def MoveTo(self, pos: glm.vec3):
		self.position = pos
		self.shouldRecalculate = True
	
	def ReinitProjectionMatrix(self, fov, aspect, zNear = -1.0, zFar = 10.0):
		self.fov = fov
		self.aspect = aspect
		self.zNear = zNear
		self.zFar = zFar

		self.projectionMatrix = glm.perspective(fov, aspect, zNear, zFar)
		self.shouldRecalculate = True
		
	def RecalculateMatrices(self):
		transform = glm.translate(glm.mat4(1.0), glm.vec3(self.position.x, self.position.y, 0.0))
		self.viewMatrix = glm.inverse(transform)
		self.viewProjectionMatrix = self.projectionMatrix * self.viewMatrix

		self.shouldRecalculate = False