from __future__ import annotations
from abc import ABC
from typing import Any, Tuple
from dataclasses import dataclass, field

@dataclass
class Event(ABC):
    consumed: bool = field(default=False, init=False, repr=False)

@dataclass
class KeyDownEvent(Event):
    key: int
    mods: int
    scancode: int
    repeat: bool

@dataclass
class KeyUpEvent(Event):
    key: int

@dataclass
class ResizeEvent(Event):
    width: int
    height: int

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

@dataclass
class MouseButtonDownEvent(Event):
    button: int
    mods: int

@dataclass
class MouseButtonUpEvent(Event):
    button: int
    mods: int

@dataclass
class MouseMoveEvent(Event):
    x: int
    y: int

    @property
    def position(self) -> Tuple[int, int]:
        return (self.x, self.y)

@dataclass
class MouseScrollEvent(Event):
    x_offset: float
    y_offset: float

@dataclass
class WindowMoveEvent(Event):
    x: int
    y: int

    @property
    def position(self) -> Tuple[int, int]:
        return (self.x, self.y)

@dataclass
class WindowChangeFocusEvent(Event):
    value: bool

@dataclass
class WindowCloseEvent(Event):
    pass

@dataclass
class ToggleVsyncEvent(Event):
    state: bool

@dataclass
class ResourceLoadedEvent(Event):
    # TODO: Add proper type hint with value `Loader`
    # Cannot do this currently because of cyclic import
    loader: Any

@dataclass
class FrameEndEvent(Event):
    pass