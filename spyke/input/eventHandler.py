from .event import Event, EventType, EventCategory
from ..utils.functional import Static
from typing import List

class EventHandler(Static):
	__Events = []

	def DispatchEvent(event: Event) -> None:
		EventHandler.__Events.append(event)
	
	def GetLastEvent() -> Event:
		return EventHandler.__Events[-1]
	
	def GetEvents() -> List[Event]:
		return EventHandler.__Events
	
	def PickEventByType(eventType: EventType) -> Event:
		"""
		Returns first event that appeared and matches the given type.
		"""
		return next((x for x in EventHandler.__Events if x.Type == eventType and not x.Handled), None)
	
	def PickEventByCategory(eventCategory: EventCategory) -> Event:
		"""
		Returns first event that appeared and matches the given category.
		"""
		return next((x for x in EventHandler.__Events if x.IsInCategory(eventCategory) and not x.Handled), None)
	
	def GetEventsByType(eventType: EventType) -> List[Event]:
		"""
		Returns all events that match the given type.
		"""
		return [x for x in EventHandler.__Events if x.Type == eventType and not x.Handled]
	
	def GetEventsByCategory(eventCategory: EventCategory) -> List[Event]:
		"""
		Returns all events that belong to the given category.
		"""
		return [x for x in EventHandler.__Events if x.IsInCategory(eventCategory) and not x.Handled]
	
	def ClearEvents() -> None:
		EventHandler.__Events.clear()