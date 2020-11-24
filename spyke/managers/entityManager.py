from ..utils import Static
from .sceneManager import SceneManager

from functools import lru_cache

class EntityManager(Static):
	__Entities = {}
	__EntityNames = {}

	def CreateEntity(name: str, *components) -> str:
		_id = SceneManager.Current.CreateEntity(*components)
		EntityManager.__Entities[name] = _id
		EntityManager.__EntityNames[_id] = name

		return _id
	
	def RemoveEntity(name: str) -> None:
		_id = EntityManager.__Entities[name]
		SceneManager.Current.DeleteEntity(_id)

		del EntityManager.__Entities[name]
		del EntityManager.__EntityNames[_id]

		EntityManager.GetEntityName.cache_clear()
		EntityManager.GetEntity.cache_clear()
	
	@lru_cache
	def GetEntityName(_id: str) -> str:
		return EntityManager.__EntityNames[_id]
	
	@lru_cache
	def GetEntity(name: str) -> str:
		return EntityManager.__Entities[name]
	
	def GetEntities() -> dict:
		return EntityManager.__Entities