import typing as t

from spyke.enums import ErrorCode

__all__ = [
    'GraphicsException',
    'SpykeException',
]

class GraphicsException(Exception):
    '''
    Represents graphics related exceptions.
    '''
    
    __module__ = ''

    @t.overload
    def __init__(self, error: str) -> None: ...
    
    @t.overload
    def __init__(self, error: ErrorCode) -> None: ...
    
    @t.overload
    def __init__(self, error: int) -> None: ...
        
    def __init__(self, error: t.Union[str, ErrorCode, int]) -> None:
        error_str = ''

        if isinstance(error, ErrorCode):
            error_str = f'OpenGL error: {error.name} ({error.value})'
        elif isinstance(error, int):
            error_str = f'OpenGL error: {ErrorCode(error).name} ({error})'
        elif isinstance(error, str):
            error_str = error
        else:
            raise TypeError(
                f'Invalid argument type for "error": {type(error)}.')

        super().__init__(error_str)

class SpykeException(Exception):
    '''
    Represents exceptions that come from spyke library.
    '''
    
    __module__ = ''

    def __init__(self, message: str):
        super().__init__(message)
