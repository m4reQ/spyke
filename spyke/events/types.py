from __future__ import annotations

import abc
import typing as t
import dataclasses

@dataclasses.dataclass
class Event(abc.ABC):
    consumed: bool = dataclasses.field(default=False, init=False, repr=False)

@dataclasses.dataclass
class KeyDownEvent(Event):
    key: int
    mods: int
    scancode: int
    repeat: bool

@dataclasses.dataclass
class KeyUpEvent(Event):
    key: int

@dataclasses.dataclass
class ResizeEvent(Event):
    width: int
    height: int

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

@dataclasses.dataclass
class MouseButtonDownEvent(Event):
    button: int
    mods: int

@dataclasses.dataclass
class MouseButtonUpEvent(Event):
    button: int
    mods: int

@dataclasses.dataclass
class MouseMoveEvent(Event):
    x: int
    y: int

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

@dataclasses.dataclass
class MouseScrollEvent(Event):
    x_offset: float
    y_offset: float

@dataclasses.dataclass
class WindowMoveEvent(Event):
    x: int
    y: int

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

@dataclasses.dataclass
class WindowChangeFocusEvent(Event):
    value: bool

@dataclasses.dataclass
class WindowCloseEvent(Event):
    pass

@dataclasses.dataclass
class ToggleVsyncEvent(Event):
    state: bool

@dataclasses.dataclass
class ResourceLoadedEvent(Event):
    # TODO: Add proper type hint with value `Loader`
    # Cannot do this currently because of cyclic import
    loader: t.Any

@dataclasses.dataclass
class FrameEndEvent(Event):
    pass