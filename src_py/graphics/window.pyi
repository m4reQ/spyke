import enum
import typing as t

from spyke.events import Event

class WindowFlags(enum.IntFlag):
    DEFAULT = t.cast(int, ...)
    RESIZABLE = t.cast(int, ...)
    FULLSCREEN = t.cast(int, ...)
    BORDERLESS = t.cast(int, ...)
    TRANSPARENT_FRAMEBUFFER = t.cast(int, ...)
    CURSOR_HIDDEN = t.cast(int, ...)
    ENABLE_VSYNC = t.cast(int, ...)
    ALLOW_FILE_DROP = t.cast(int, ...)
    REQUIRE_DEPTH_STENCIL = t.cast(int, ...)

class ResizeEventData:
    width: int
    height: int

    @property
    def size(self) -> tuple[int, int]: ...

class ButtonUpEventData:
    x: int
    y: int
    button: int
    modifiers: int

    @property
    def position(self) -> tuple[int, int]: ...

class ButtonDownEventData:
    x: int
    y: int
    button: int
    modifiers: int

    @property
    def position(self) -> tuple[int, int]: ...

class CharEventData:
    repeat_count: int
    scan_code: int
    was_pressed: bool

    @property
    def character(self) -> str: ...

class KeyUpEventData:
    key: int
    scan_code: int

class KeyDownEventData:
    key: int
    repeat_count: int
    scan_code: int
    was_pressed: bool

class ScrollEventData:
    x: int
    y: int
    delta: int
    modifiers: int

    @property
    def position(self) -> tuple[int, int]: ...

class ShowEventData:
    is_visible: bool


class MouseMoveEventData:
    x: int
    y: int
    modifiers: int

    @property
    def position(self) -> tuple[int, int]: ...

class CloseEventData:
    time: float

class MoveEventData:
    x: int
    y: int

    @property
    def position(self) -> tuple[int, int]: ...

class WindowSettings:
    width: int
    height: int
    title: str
    flags: int

    def __init__(self,
                 width: int,
                 height: int,
                 title: str,
                 flags: WindowFlags = WindowFlags.DEFAULT) -> None: ...

resize_event: Event[ResizeEventData]
move_event: Event[MoveEventData]
close_event: Event[CloseEventData]
mouse_move_event: Event[MouseMoveEventData]
show_event: Event[ShowEventData]
scroll_event: Event[ScrollEventData]
key_down_event: Event[KeyDownEventData]
key_up_event: Event[KeyUpEventData]
button_down_event: Event[ButtonDownEventData]
button_up_event: Event[ButtonUpEventData]
char_event: Event[CharEventData]

def initialize(settings: WindowSettings, /) -> None: ...
def shutdown() -> None: ...
def get_width() -> int: ...
def get_height() -> int: ...
def get_size() -> tuple[int, int]: ...
def get_x() -> int: ...
def get_y() -> int: ...
def get_position() -> tuple[int, int]: ...
def is_visible() -> bool: ...
def should_close() -> bool: ...
def set_title(title: str, /) -> None: ...
def resize(width: int, height: int, /) -> None: ...
def move(x: int, y: int, /) -> None: ...
def swap_buffers() -> None: ...
def process_events() -> None: ...
def get_open_directory(window_title: str | None = None, initial_dir: str | None = None) -> str | None: ...
