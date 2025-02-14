import dataclasses

from spyke.ecs.components.component import Component


@dataclasses.dataclass(eq=False)
class TagComponent(Component):
	name: str
