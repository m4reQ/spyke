class GraphicsException(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class NovaException(Exception):
    def __init__(self, message: str):
        super().__init__(message)