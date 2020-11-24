from ..utils import Static
from ..ecs import Scene

from functools import lru_cache

class SceneManager(Static):
	Current: Scene = None
	SceneName = ""
	
	def CreateScene(name: str, timed: bool = False) -> Scene:
		"""
		Creates a new scene, sets it as current and returns
		scene instance.
		"""

		s = Scene(timed)
		SceneManager.Current = s
		SceneManager.SceneName = name
		
		return s
	