from .aBuffer import AMappable
from ...exceptions import GraphicsException

class MultiBuffer(AMappable):
    def __init__(self, size: int, buffersCount: int):
        super().__init__(size, None)

        if size % buffersCount != 0:
            raise GraphicsException(f"Cannot equally divide buffer of size {size}.")