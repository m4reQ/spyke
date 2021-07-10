class GraphicsException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class SpykeException(Exception):
    def __init__(self, message: str):
        super().__init__(message)