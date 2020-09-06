from .components.spriteComponent import Sprite
from .components.audioComponent import AudioComponent
from .entityManager import EntityManager
from ..enums import ComponentType

import uuid

class Entity(object):
	def __init__(self, name: str):
		self.__components = {}
		self.name = name
		self.id = uuid.uuid1().int

		EntityManager.RegisterEntity(self)

	def AddComponent(self, componentType: ComponentType, *args):
		if componentType == ComponentType.Sprite:
			component = Sprite()
		elif componentType == ComponentType.Audio:
			component = AudioComponent(args[0])
		else:
			raise RuntimeError("Invalid entity component type.")
		
		self.__components[componentType] = component

	def OnRender(self):
		pass
	
	def OnUpdate(self, deltaTime: float):
		pass
	
	def OnLoad(self):
		pass
	
	def OnUnload(self):
		pass

	@property
	def SpriteComponent(self):
		return self.__components[ComponentType.Sprite]