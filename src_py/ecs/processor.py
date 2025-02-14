from __future__ import annotations

import abc
import typing as t

if t.TYPE_CHECKING:
    from spyke.ecs.scene import Scene

class Processor(abc.ABC):
    @abc.abstractmethod
    def process(self, scene: 'Scene', *args: t.Any, **kwargs: t.Any) -> None:
        pass
