from spyke.enums import MagFilter, MinFilter, WrapMode


class TextureSpec:
    __slots__ = (
        '__weakref__',
        'mipmaps',
        'min_filter',
        'mag_filter',
        'wrap_mode',
        'compress'
    )

    def __init__(self):
        self.mipmaps: int = 3
        self.min_filter: MinFilter = MinFilter.LinearMipmapLinear
        self.mag_filter: MagFilter = MagFilter.Linear
        self.wrap_mode: WrapMode = WrapMode.Repeat
        self.compress: bool = False
