import enum

import glfw  # type: ignore[import-untyped]


class MouseButton(enum.IntEnum):
    Left = glfw.MOUSE_BUTTON_LEFT
    Middle = glfw.MOUSE_BUTTON_MIDDLE
    Right = glfw.MOUSE_BUTTON_RIGHT


class KeyMod(enum.IntFlag):
    Control = glfw.MOD_CONTROL
    Shift = glfw.MOD_SHIFT
    Alt = glfw.MOD_ALT
    Super = glfw.MOD_SUPER
    CapsLock = glfw.MOD_CAPS_LOCK
    NumLock = glfw.MOD_NUM_LOCK


class Key(enum.IntEnum):
    Unknown = glfw.KEY_UNKNOWN

    # special
    Space = glfw.KEY_SPACE
    Apostrophe = glfw.KEY_APOSTROPHE
    Comma = glfw.KEY_COMMA
    Minus = glfw.KEY_MINUS
    Period = glfw.KEY_PERIOD
    Slash = glfw.KEY_SLASH
    Semicolon = glfw.KEY_SEMICOLON
    LeftBracket = glfw.KEY_LEFT_BRACKET
    RightBracket = glfw.KEY_RIGHT_BRACKET
    Backslash = glfw.KEY_BACKSLASH
    Grave = glfw.KEY_GRAVE_ACCENT
    Escape = glfw.KEY_ESCAPE
    Enter = glfw.KEY_ENTER
    KeypadEnter = glfw.KEY_KP_ENTER
    Tab = glfw.KEY_TAB
    Backspace = glfw.KEY_BACKSPACE
    Insert = glfw.KEY_INSERT
    Delete = glfw.KEY_DELETE
    PageUp = glfw.KEY_PAGE_UP
    PageDown = glfw.KEY_PAGE_DOWN
    Home = glfw.KEY_HOME
    End = glfw.KEY_END
    CapsLock = glfw.KEY_CAPS_LOCK
    ScrollLock = glfw.KEY_SCROLL_LOCK
    NumLock = glfw.KEY_NUM_LOCK
    PrintScreen = glfw.KEY_PRINT_SCREEN
    Pause = glfw.KEY_PAUSE
    Menu = glfw.KEY_MENU

    # functional
    F1 = glfw.KEY_F1
    F2 = glfw.KEY_F2
    F3 = glfw.KEY_F3
    F4 = glfw.KEY_F4
    F5 = glfw.KEY_F5
    F6 = glfw.KEY_F6
    F7 = glfw.KEY_F7
    F8 = glfw.KEY_F8
    F9 = glfw.KEY_F9
    F10 = glfw.KEY_F10
    F11 = glfw.KEY_F11
    F12 = glfw.KEY_F12

    # modifiers
    LeftShift = glfw.KEY_LEFT_SHIFT
    RightShift = glfw.KEY_RIGHT_SHIFT
    LeftControl = glfw.KEY_LEFT_CONTROL
    RightControl = glfw.KEY_RIGHT_CONTROL
    LeftAlt = glfw.KEY_LEFT_ALT
    RightAlt = glfw.KEY_RIGHT_ALT
    LeftSuper = glfw.KEY_LEFT_SUPER
    RightSuper = glfw.KEY_RIGHT_SUPER

    # arrows
    Right = glfw.KEY_RIGHT
    Left = glfw.KEY_LEFT
    Up = glfw.KEY_UP
    Down = glfw.KEY_DOWN

    # numerical
    _0 = glfw.KEY_0
    _1 = glfw.KEY_1
    _2 = glfw.KEY_2
    _3 = glfw.KEY_3
    _4 = glfw.KEY_4
    _5 = glfw.KEY_5
    _6 = glfw.KEY_6
    _7 = glfw.KEY_7
    _8 = glfw.KEY_8
    _9 = glfw.KEY_9

    # alphabetical
    A = glfw.KEY_A
    B = glfw.KEY_B
    C = glfw.KEY_C
    D = glfw.KEY_D
    E = glfw.KEY_E
    F = glfw.KEY_F
    G = glfw.KEY_G
    H = glfw.KEY_H
    I = glfw.KEY_I
    J = glfw.KEY_J
    K = glfw.KEY_K
    L = glfw.KEY_L
    M = glfw.KEY_M
    N = glfw.KEY_N
    O = glfw.KEY_O
    P = glfw.KEY_P
    Q = glfw.KEY_Q
    R = glfw.KEY_R
    S = glfw.KEY_S
    T = glfw.KEY_T
    U = glfw.KEY_U
    V = glfw.KEY_V
    W = glfw.KEY_W
    X = glfw.KEY_X
    Y = glfw.KEY_Y
    Z = glfw.KEY_Z
