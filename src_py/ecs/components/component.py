import abc
import dataclasses


@dataclasses.dataclass(eq=False, slots=True)
class Component(abc.ABC):
    pass
