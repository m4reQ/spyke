import abc
import logging

from OpenGL import GL


class OpenglObjectBase(abc.ABC):
    def __init__(self):
        super().__init__()

        self._id = GL.GLuint()
        self._is_initialized = False
        self._is_deleted = False

        _objects.append(self)

    def __str__(self):
        return f'{type(self).__name__} (id: {self._id.value})'

    def __repr__(self):
        return str(self)

    def initialize(self) -> None:
        pass

    def delete(self) -> None:
        self._is_deleted = True

    def ensure_initialized(self) -> None:
        if self._is_deleted:
            raise ObjectDeletedException(self)

        if not self._is_initialized:
            self._initialize()

    @property
    def is_initialized(self) -> bool:
        return self._is_initialized

    @property
    def id(self) -> int:
        return self._id.value

    def _initialize(self) -> None:
        self.initialize()
        self._is_initialized = True
        _logger.info('Object %s initialized succesfully.', self)

class ObjectDeletedException(RuntimeError):
    '''
    Exception raised when user tries to use an OpenGL object that
    has been already deleted.
    '''

    def __init__(self, obj: OpenglObjectBase) -> None:
        super().__init__(f'Tried to use OpenGL object {obj} that has been already deleted.')

def delete_all() -> None:
    '''
    Disposes all OpenGL objects, making sure no graphics resources are
    left alive and its safe to close an application.
    After this function is called it is impossible to reuse any objects. Any
    attempts to reinitialize them will result in `ObjectDeletedException` being thrown.
    This is to ensure no unexpected behavior can occur.
    '''

    for obj in _objects:
        obj.delete()

        _logger.info('OpenGL object %s has been successfully deleted.', obj)

    _objects.clear()

def delete_object(obj: OpenglObjectBase) -> None:
    '''
    Deletes single OpenGL object and removes it's reference from objects
    registry. Deletion should always be done using this function to prevent
    further attempts to delete object by automatic cleanup.

    @obj: OpenGL object that is going to be delted.
    '''

    obj.delete()

    if obj in _objects:
        _objects.remove(obj)

_objects: list[OpenglObjectBase] = []
_logger = logging.getLogger(__name__)
