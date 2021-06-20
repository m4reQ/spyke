"""
Changes made by m4reQ:
- renamed Scene to Scene
- changed time measurement function from time.process_time to time.perf_counter
- changed names of public functions to use PascalCase naming convention
- changed Scene.AddComponent function ability to set component's reference to a parent entity and scene if component type is ScriptComponent
- using ints casted to str as ids for entities (this is mainly because an internal CPython optimization for string dictionary keys)
- added type hint to 'world' member in Processor class
- moved Processor class below Scene class
- added 'timed' memeber in Scene class that indicates if it uses timed processing
- renamed 'world' Processors, class attribute to 'scene'
- added 'LateInit' method to Processor class. It is called after an object gets it's scene reference and is generally initialized.
- added Current global variable that indicates current scene
- added Scene.MakeCurrent method that sets scene as the current
- added Scene.name member that is just a scene name
- removed timing methods of Scene class
"""

from functools import lru_cache as _lru_cache
from typing import List as _List
from typing import Type as _Type
from typing import TypeVar as _TypeVar
from typing import Any as _Any
from typing import Tuple as _Tuple
from typing import Iterable as _Iterable

from .components.script import ScriptComponent

version = '1.3'

C = _TypeVar('C')
P = _TypeVar('P')

class Processor:
	pass

class Scene:
	"""A Scene object keeps track of all Entities, Components, and Processors.

	A Scene contains a database of all Entity/Component assignments. The Scene
	is also responsible for executing all Processors assigned to it for each
	frame of your game.
	"""

	Current = None

	def __init__(self, name = ""):
		self._processors = []
		self._next_entity_id = 0
		self._components = {}
		self._entities = {}
		self._dead_entities = set()
		self.name = name

	def clear_cache(self) -> None:
		self.GetComponent.cache_clear()
		self.GetComponents.cache_clear()

	def ClearDatabase(self) -> None:
		"""Remove all Entities and Components from the Scene."""
		self._next_entity_id = 0
		self._dead_entities.clear()
		self._components.clear()
		self._entities.clear()
		self.clear_cache()

	def AddProcessor(self, processor_instance: Processor, priority=0) -> None:
		"""Add a Processor instance to the Scene.

		:param processor_instance: An instance of a Processor,
			   subclassed from the Processor class
		:param priority: A higher number is processed first.
		"""
		assert issubclass(processor_instance.__class__, Processor)
		processor_instance.priority = priority
		processor_instance.scene = self
		processor_instance.LateInit()
		self._processors.append(processor_instance)
		self._processors.sort(key=lambda proc: proc.priority, reverse=True)

	def RemoveProcessor(self, processor_type: Processor) -> None:
		"""Remove a Processor from the Scene, by type.

		:param processor_type: The class type of the Processor to remove.
		"""
		for processor in self._processors:
			if type(processor) == processor_type:
				processor.world = None
				self._processors.remove(processor)

	def GetProcessor(self, processor_type: _Type[P]) -> P:
		"""Get a Processor instance, by type.

		This method returns a Processor instance by type. This could be
		useful in certain situations, such as wanting to call a method on a
		Processor, from within another Processor.

		:param processor_type: The type of the Processor you wish to retrieve.
		:return: A Processor instance that has previously been added to the Scene.
		"""
		for processor in self._processors:
			if type(processor) == processor_type:
				return processor

	def CreateEntity(self, *components) -> str:
		"""Create a new Entity.

		This method returns an Entity ID, which is just a plain integer.
		You can optionally pass one or more Component instances to be
		assigned to the Entity.

		:param components: Optional components to be assigned to the
			   entity on creation.
		:return: The next Entity ID in sequence.
		"""
		self._next_entity_id += 1

		entId = str(self._next_entity_id)

		if entId not in self._entities:
			self._entities[entId] = {}

		# TODO: duplicate AddComponent code here for performance
		for component in components:
			self.AddComponent(entId, component)

		# self.clear_cache()
		return entId

	def DeleteEntity(self, entity: str, immediate=False) -> None:
		"""Delete an Entity from the Scene.

		Delete an Entity and all of it's assigned Component instances from
		the world. By default, Entity deletion is delayed until the next call
		to *Scene.process*. You can request immediate deletion, however, by
		passing the "immediate=True" parameter. This should generally not be
		done during Entity iteration (calls to Scene.get_component/s).

		Raises a KeyError if the given entity does not exist in the database.
		:param entity: The Entity ID you wish to delete.
		:param immediate: If True, delete the Entity immediately.
		"""
		if immediate:
			for component_type in self._entities[entity]:
				self._components[component_type].discard(entity)

				if not self._components[component_type]:
					del self._components[component_type]

			del self._entities[entity]
			self.clear_cache()

		else:
			self._dead_entities.add(entity)

	def EntityExists(self, entity: str) -> bool:
		"""Check if a specific entity exists.

		Empty entities(with no components) and dead entities(destroyed
		by delete_entity) will not count as existent ones.
		:param entity: The Entity ID to check existance for.
		:return: True if the entity exists, False otherwise.
		"""
		return entity in self._entities and entity not in self._dead_entities

	def ComponentForEntity(self, entity: str, component_type: _Type[C]) -> C:
		"""Retrieve a Component instance for a specific Entity.

		Retrieve a Component instance for a specific Entity. In some cases,
		it may be necessary to access a specific Component instance.
		For example: directly modifying a Component to handle user input.

		Raises a KeyError if the given Entity and Component do not exist.
		:param entity: The Entity ID to retrieve the Component for.
		:param component_type: The Component instance you wish to retrieve.
		:return: The Component instance requested for the given Entity ID.
		"""
		return self._entities[entity][component_type]

	def ComponentsForEntity(self, entity: str) -> _Tuple[C, ...]:
		"""Retrieve all Components for a specific Entity, as a Tuple.

		Retrieve all Components for a specific Entity. The method is probably
		not appropriate to use in your Processors, but might be useful for
		saving state, or passing specific Components between Scene instances.
		Unlike most other methods, this returns all of the Components as a
		Tuple in one batch, instead of returning a Generator for iteration.

		Raises a KeyError if the given entity does not exist in the database.
		:param entity: The Entity ID to retrieve the Components for.
		:return: A tuple of all Component instances that have been
		assigned to the passed Entity ID.
		"""
		return tuple(self._entities[entity].values())

	def HasComponent(self, entity: str, component_type: _Any) -> bool:
		"""Check if a specific Entity has a Component of a certain type.

		:param entity: The Entity you are querying.
		:param component_type: The type of Component to check for.
		:return: True if the Entity has a Component of this type,
				 otherwise False
		"""
		return component_type in self._entities[entity]

	def HasComponents(self, entity: str, *component_types: _Any) -> bool:
		"""Check if an Entity has all of the specified Component types.

		:param entity: The Entity you are querying.
		:param component_types: Two or more Component types to check for.
		:return: True if the Entity has all of the Components,
				 otherwise False
		"""
		return all(comp_type in self._entities[entity] for comp_type in component_types)

	def AddComponent(self, entity: str, component_instance: _Any) -> None:
		"""Add a new Component instance to an Entity.

		Add a Component instance to an Entiy. If a Component of the same type
		is already assigned to the Entity, it will be replaced.

		:param entity: The Entity to associate the Component with.
		:param component_instance: A Component instance.
		"""
		component_type = type(component_instance)

		if component_type == ScriptComponent:
			component_instance.entity = entity
			component_instance.world = self

		if component_type not in self._components:
			self._components[component_type] = set()

		self._components[component_type].add(entity)

		self._entities[entity][component_type] = component_instance
		self.clear_cache()

	def RemoveComponent(self, entity: str, component_type: _Any) -> int:
		"""Remove a Component instance from an Entity, by type.

		A Component instance can be removed by providing it's type.
		For example: world.delete_component(enemy_a, Velocity) will remove
		the Velocity instance from the Entity enemy_a.

		Raises a KeyError if either the given entity or Component type does
		not exist in the database.
		:param entity: The Entity to remove the Component from.
		:param component_type: The type of the Component to remove.
		"""
		self._components[component_type].discard(entity)

		if not self._components[component_type]:
			del self._components[component_type]

		del self._entities[entity][component_type]

		if not self._entities[entity]:
			del self._entities[entity]

		self.clear_cache()
		return entity

	def _get_component(self, component_type: _Type[C]) -> _Iterable[_Tuple[int, C]]:
		"""Get an iterator for Entity, Component pairs.

		:param component_type: The Component type to retrieve.
		:return: An iterator for (Entity, Component) tuples.
		"""
		entity_db = self._entities

		for entity in self._components.get(component_type, []):
			yield entity, entity_db[entity][component_type]

	def _get_components(self, *component_types: _Type) -> _Iterable[_Tuple[int, ...]]:
		"""Get an iterator for Entity and multiple Component sets.

		:param component_types: Two or more Component types.
		:return: An iterator for Entity, (Component1, Component2, etc)
		tuples.
		"""
		entity_db = self._entities
		comp_db = self._components

		try:
			for entity in set.intersection(*[comp_db[ct] for ct in component_types]):
				yield entity, [entity_db[entity][ct] for ct in component_types]
		except KeyError:
			pass

	@_lru_cache()
	def GetComponent(self, component_type: _Type[C]) -> _List[_Tuple[int, C]]:
		return [query for query in self._get_component(component_type)]

	@_lru_cache()
	def GetComponents(self, *component_types: _Type):
		return [query for query in self._get_components(*component_types)]

	def TryComponent(self, entity: str, component_type: _Type):
		"""Try to get a single component type for an Entity.

		This method will return the requested Component if it exists, but
		will pass silently if it does not. This allows a way to access
		optional Components that may or may not exist, without having to
		first querty the Entity to see if it has the Component type.

		:param entity: The Entity ID to retrieve the Component for.
		:param component_type: The Component instance you wish to retrieve.
		:return: A iterator containg the single Component instance requested,
				 which is empty if the component doesn't exist.
		"""
		if component_type in self._entities[entity]:
			yield self._entities[entity][component_type]
		else:
			return None

	def TryComponents(self, entity: str, *component_types: _Type):
		"""Try to get a multiple component types for an Entity.

		This method will return the requested Components if they exist, but
		will pass silently if they do not. This allows a way to access
		optional Components that may or may not exist, without first having
		to query if the entity has the Component types.

		:param entity: The Entity ID to retrieve the Component for.
		:param component_types: The Components types you wish to retrieve.
		:return: A iterator containg the multiple Component instances requested,
				 which is empty if the components do not exist.
		"""
		if all(comp_type in self._entities[entity] for comp_type in component_types):
			yield [self._entities[entity][comp_type] for comp_type in component_types]
		else:
			return None

	def _clear_dead_entities(self):
		"""Finalize deletion of any Entities that are marked dead.
		
		In the interest of performance, this method duplicates code from the
		`delete_entity` method. If that method is changed, those changes should
		be duplicated here as well.
		"""
		for entity in self._dead_entities:

			for component_type in self._entities[entity]:
				self._components[component_type].discard(entity)

				if not self._components[component_type]:
					del self._components[component_type]

			del self._entities[entity]

		self._dead_entities.clear()
		self.clear_cache()

	def Process(self, *args, **kwargs):
		"""Call the process method on all Processors, in order of their priority.

		Call the *process* method on all assigned Processors, respecting their
		optional priority setting. In addition, any Entities that were marked
		for deletion since the last call to *Scene.process*, will be deleted
		at the start of this method call.

		:param args: Optional arguments that will be passed through to the
					 *process* method of all Processors.
		"""
		self._clear_dead_entities()
		for processor in self._processors:
			processor.Process(*args, **kwargs)
	
	def MakeCurrent(self):
		Scene.Current = self

class Processor:
	"""Base class for all Processors to inherit from.

	Processor instances must contain a `Process` method. Other than that,
	you are free to add any additional methods that are necessary. The process
	method will be called by each call to `Scene.Process`, so you will
	generally want to iterate over entities with one (or more) calls to the
	appropriate world methods there, such as
	`for ent, (rend, vel) in self.world.get_components(Renderable, Velocity):`
	"""
	scene: Scene = None

	def LateInit(self, *args, **kwargs):
		pass

	def Process(self, *args, **kwargs):
		raise NotImplementedError

from .processors import TransformProcessor, ScriptProcessor, ParticleProcessor

def CreateScene(name: str):
	s = Scene(name)
	s.AddProcessor(TransformProcessor())
	s.AddProcessor(ParticleProcessor())
	s.AddProcessor(ScriptProcessor())
	return s