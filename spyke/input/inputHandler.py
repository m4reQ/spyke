from ..utils import Static
from ..window.window import Window

import glfw
from typing import Tuple

class InputHandler(Static):
    __Window = None
    
    def Initialize(window: Window) -> None:
        InputHandler.__Window = window

    def IsKeyPressed(keyCode: int) -> bool:
        state = glfw.get_key(InputHandler.__Window.WindowHandle, keyCode)

        return state == glfw.PRESS or state == glfw.REPEAT

    def IsMouseButtonPressed(button: int) -> bool:
        state = glfw.get_mouse_button(InputHandler.__Window.WindowHandle, button)

        return state == glfw.PRESS
    
    def GetMousePosition() -> Tuple[float, float]:
        return glfw.get_cursor_pos(InputHandler.__Window.WindowHandle)