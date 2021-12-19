from spyke.enums import ErrorCode
from typing import Union

class GraphicsException(Exception):
    def __init__(self, error: Union[str, ErrorCode, int]):
        error_str = ''

        if isinstance(error, ErrorCode):
            error_str = f'OpenGL error: {error.name} ({error.value})'
        elif isinstance(error, int):
            error_str = f'OpenGL error: {ErrorCode(error).name} ({error})'
        elif isinstance(error, str):
            error_str = error
        else:
            raise TypeError(f'Invalid argument type for "error": {type(error)}.')
        
        super().__init__(error_str)

class SpykeException(Exception):
    def __init__(self, message: str):
        super().__init__(message)