from ...autoslot import WeakSlots
import glm

class CameraType:
	Orthographic, Perspective = range(2)

class CameraComponent(WeakSlots):
	@staticmethod
	def _CreateOrtho():
		pass

	@staticmethod
	def _CreatePerspective():
		pass

	def __init__(self, cameraType: CameraType):
		self.isPrimary = False
		
		self.shouldRecalculate = False

		self._projectionMatrix = glm.mat4(1.0)
		self._viewMatrix = glm.mat4(1.0)
		self._viewProjectionMatrix = glm.mat4(1.0)

		if cameraType == CameraType.Orthographic:
			self._projectionFunc = CameraComponent._CreateOrtho
		else:
			self._projectionFunc = CameraComponent._CreatePerspective