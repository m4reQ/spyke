import dataclasses

from spyke.ecs import Component


@dataclasses.dataclass
class TagComponent(Component):
	name: str
