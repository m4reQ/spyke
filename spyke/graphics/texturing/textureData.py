import typing

if typing.TYPE_CHECKING:
    from spyke.enums import TextureFormat
    import numpy as np


class TextureData:
    __slots__ = (
        '__weakref__',
        'width',
        'height',
        'data',
        'format',
        'filepath'
    )

    def __init__(self, width: int, height: int):
        self.width: int = width
        self.height: int = height
        self.data: np.ndarray = None
        self.format: TextureFormat = TextureFormat.Rgba
        self.filepath: str = ''
