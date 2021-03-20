from .memory import GLMarshal

class GraphicsException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

        GLMarshal.ReleaseAll()

class NovaException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

        GLMarshal.ReleaseAll()