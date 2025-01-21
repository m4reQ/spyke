import dataclasses

from spyke.ecs import Component


@dataclasses.dataclass(eq=False)
class TagComponent(Component):
	name: str
