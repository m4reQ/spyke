from dataclasses import dataclass
from typing import Optional

@dataclass
class WindowSpecs:
    '''
    A structure used to configure window.
    '''

    width: int
    height: int
    title: str
    samples: int = 1
    vsync: bool = True
    resizable: bool = True
    fullscreen: bool = False
    borderless: bool = False
    cursor_visible: bool = True
    icon_filepath: Optional[str] = None
