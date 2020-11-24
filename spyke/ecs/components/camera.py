from ...enums import CameraType
from ...graphics.cameras import OrthographicCamera

class CameraComponent(object):
	def __init__(self, cameraType: CameraType, left: float, right: float, bottom: float, top: float, zNear = -1.0, zFar = 10.0):
		if cameraType == CameraType.Orthographic:
			self.Camera = OrthographicCamera(left, right, bottom, top, zNear, zFar)
		else:
			raise RuntimeError("Invalid camera type")