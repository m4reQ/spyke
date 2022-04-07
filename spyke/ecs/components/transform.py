import glm

class TransformComponent:
    __slots__ = (
        '__weakref__',
        '_pos',
        '_size',
        '_rot',
        '_rot_hint',
        '_pos_changed',
        '_size_changed',
        '_rot_changed',
        'matrix',
        '_trans_mat',
        '_scale_mat',
        '_rot_quat'
    )

    def __init__(self, position: glm.vec3, size: glm.vec3, rotation: glm.vec3):
        self._pos: glm.vec3 = position
        self._size: glm.vec3 = size
        self._rot: glm.vec3 = rotation % 360.0
        self._rot_hint = rotation

        self._pos_changed: bool = True
        self._size_changed: bool = True
        self._rot_changed: bool = True

        self.matrix: glm.mat4 = glm.mat4(1.0)

        self._trans_mat: glm.mat4 = glm.mat4(1.0)
        self._scale_mat: glm.mat4 = glm.mat4(1.0)
        self._rot_quat: glm.quat = glm.quat(glm.radians(self._rot))

        self.recalculate()

    def recalculate(self) -> None:
        if self._pos_changed:
            self._trans_mat = glm.translate(glm.mat4(1.0), self._pos)
            self._pos_changed = False

        if self._rot_changed:
            self._rot_quat = glm.quat(glm.radians(self._rot))
            self._rot_changed = False

        if self._size_changed:
            self._scale_mat = glm.scale(glm.mat4(1.0), self._size)
            self._size_changed = False

        self.matrix = self._trans_mat * \
            glm.mat4_cast(self._rot_quat) * self._scale_mat

    @property
    def should_recalculate(self) -> bool:
        return any([self._pos_changed, self._size_changed, self._rot_changed])

    @property
    def position(self) -> glm.vec3:
        return self._pos

    @position.setter
    def position(self, val: glm.vec3) -> None:
        self._pos = val
        self._pos_changed = True

    @property
    def size(self) -> glm.vec3:
        return self._size

    @size.setter
    def size(self, val: glm.vec3) -> None:
        self._size = val
        self._size_changed = True

    @property
    def rotation(self) -> glm.vec3:
        return self._rot

    @rotation.setter
    def rotation(self, val: glm.vec3):
        self._rot = val % 360.0
        self._rot_hint = val
        self._rot_changed = True
