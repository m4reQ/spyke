from ..utils import Static

from functools import lru_cache

IMPORTED = False

class SceneManager(Static):
	Current = None
	SceneName = ""
	CurrentSceneChanged = False
	
	def CreateScene(name: str, timed: bool = False):
		"""
		Creates a new scene, sets it as current and returns
		scene instance.
		"""

		if not IMPORTED:
			from ..ecs import Scene

		s = Scene(timed)
		SceneManager.Current = s
		SceneManager.SceneName = name

		return s
	