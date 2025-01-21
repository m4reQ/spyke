import enum

class Key(enum.IntEnum):
    NUM_0: int
    NUM_1: int
    NUM_2: int
    NUM_3: int
    NUM_4: int
    NUM_5: int
    NUM_6: int
    NUM_7: int
    NUM_8: int
    NUM_9: int
    A: int
    B: int
    C: int
    D: int
    E: int
    F: int
    G: int
    H: int
    I: int
    J: int
    K: int
    L: int
    M: int
    N: int
    O: int
    P: int
    Q: int
    R: int
    S: int
    T: int
    U: int
    V: int
    W: int
    X: int
    Y: int
    Z: int
    CANCEL: int
    BACK: int
    TAB: int
    CLEAR: int
    RETURN: int
    SHIFT: int
    CONTROL: int
    MENU: int
    PAUSE: int
    CAPITAL: int
    KANA: int
    HANGUL: int
    IME_ON: int
    JUNJA: int
    FINAL: int
    HANJA: int
    KANJI: int
    IME_OFF: int
    ESCAPE: int
    CONVERT: int
    NONCONVERT: int
    ACCEPT: int
    MODECHANGE: int
    SPACE: int
    PRIOR: int
    NEXT: int
    END: int
    HOME: int
    LEFT: int
    UP: int
    RIGHT: int
    DOWN: int
    SELECT: int
    PRINT: int
    EXECUTE: int
    SNAPSHOT: int
    INSERT: int
    DELETE: int
    HELP: int
    LWIN: int
    RWIN: int
    APPS: int
    SLEEP: int
    NUMPAD0: int
    NUMPAD1: int
    NUMPAD2: int
    NUMPAD3: int
    NUMPAD4: int
    NUMPAD5: int
    NUMPAD6: int
    NUMPAD7: int
    NUMPAD8: int
    NUMPAD9: int
    MULTIPLY: int
    ADD: int
    SEPARATOR: int
    SUBTRACT: int
    DECIMAL: int
    DIVIDE: int
    F1: int
    F2: int
    F3: int
    F4: int
    F5: int
    F6: int
    F7: int
    F8: int
    F9: int
    F10: int
    F11: int
    F12: int
    F13: int
    F14: int
    F15: int
    F16: int
    F17: int
    F18: int
    F19: int
    F20: int
    F21: int
    F22: int
    F23: int
    F24: int
    NUMLOCK: int
    SCROLL: int
    LSHIFT: int
    RSHIFT: int
    LCONTROL: int
    RCONTROL: int
    LMENU: int
    RMENU: int
    BROWSER_BACK: int
    BROWSER_FORWARD: int
    BROWSER_REFRESH: int
    BROWSER_STOP: int
    BROWSER_SEARCH: int
    BROWSER_FAVORITES: int
    BROWSER_HOME: int
    VOLUME_MUTE: int
    VOLUME_DOWN: int
    VOLUME_UP: int
    MEDIA_NEXT_TRACK: int
    MEDIA_PREV_TRACK: int
    MEDIA_STOP: int
    MEDIA_PLAY_PAUSE: int
    LAUNCH_MAIL: int
    LAUNCH_MEDIA_SELECT: int
    LAUNCH_APP1: int
    LAUNCH_APP2: int

class Button(enum.IntEnum):
    X1: int
    X2: int
    LEFT: int
    RIGHT: int
    MIDDLE: int

class Modifier(enum.IntFlag):
    CONTROL: int
    SHIFT: int

def is_key_down(key: Key | str, /) -> bool: ...
def is_key_up(key: Key | str, /) -> bool: ...
def is_button_up(button: Button, /) -> bool: ...
def is_button_down(button: Button, /) -> bool: ...
def get_mouse_x() -> int: ...
def get_mouse_y() -> int: ...
def get_mouse_position() -> tuple[int, int]: ...
def get_modifiers() -> int: ...
def is_modifier_active(modifier: int, /) -> bool: ...
def begin_text_input() -> None: ...
def end_text_input() -> str: ...
def get_text_input() -> str: ...
def clear_text_input() -> None: ...
def is_text_input_active() -> bool: ...
