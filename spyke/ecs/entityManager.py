from .entity import Entity
from ..debug import Log, LogLevel

class EntityManager(object):
	__SpriteComponents = []

	__Entities = []
	
	@staticmethod
	def Initialize():
		pass

	@staticmethod
	def RegisterEntity(entity: Entity):
		EntityManager.__Entities.append(entity)
		entity.OnLoad()

		try:
			EntityManager.__SpriteComponents.append(entity.SpriteComponent)
		except KeyError:
			pass
		
		Log(f"Entity '{entity.name}' (id: {entity.id}) registered.", LogLevel.Info)
	
	@staticmethod
	def UnregisterEntity(entity: Entity):
		EntityManager.__Entities.remove(entity)
		entity.OnUnload()

	@staticmethod
	def Update(deltaTime: float):
		for entity in EntityManager.__Entities:
			entity.OnUpdate(deltaTime)
	
	@staticmethod
	def Render():
		for sprite in EntityManager.__SpriteComponents:
			sprite.OnRender()
