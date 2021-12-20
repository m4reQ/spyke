import glm

class CameraType:
	Orthographic, Perspective = range(2)

class CameraComponent:
	__slots__ = (
		'__weakref__',
		'is_primary',
		'should_recalculate',
		'_projection_matrix',
		'_view_matrix',
		'_view_projection_matrix',
		'_projection_func'
	)
	
	@staticmethod
	def _CreateOrtho():
		pass

	@staticmethod
	def _CreatePerspective():
		pass

	def __init__(self, camera_type: CameraType):
		self.is_primary = False
		
		self.should_recalculate = False

		self._projection_matrix = glm.mat4(1.0)
		self._view_matrix = glm.mat4(1.0)
		self._view_projection_matrix = glm.mat4(1.0)

		if camera_type == CameraType.Orthographic:
			self._projection_func = CameraComponent._CreateOrtho
		else:
			self._projection_func = CameraComponent._CreatePerspective