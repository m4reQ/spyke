from ...graphics.cameras import ACamera
import glm

class CameraComponent(object):
	def __init__(self, cameraObject: ACamera):
		if not isinstance(cameraObject, ACamera):
			raise ValueError("Invalid camera object given.")
		else:
			self.camera = cameraObject

class NEW___CameraComponent(object):
	def __init__(self, cameraObject: ACamera):
		if not isinstance(cameraObject, ACamera):
			raise ValueError("Invalid camera object given.")
		else:
			self.camera = cameraObject

		self.isPrimary = False
		
		self.shouldRecalculate = False

		self._projectionMatrix = glm.mat4(1.0)
		self._viewMatrix = glm.mat4(1.0)
		self._viewProjectionMatrix = glm.mat4(1.0)