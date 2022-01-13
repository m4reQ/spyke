import glm
from typing import Tuple, Union
from spyke.exceptions import SpykeException
from glm import vec2 as Vector2, vec3 as Vector3, vec4 as Vector4, mat4 as Matrix4


def create_translation(pos: Union[glm.vec3, Tuple[float, float, float]]) -> glm.mat4:
    return glm.translate(glm.mat4(1.0), glm.vec3(pos))


def create_scale(size: Union[glm.vec3, Tuple[float, float, float]]) -> glm.mat4:
    return glm.scale(glm.mat4(1.0), glm.vec3(size))


def create_rotation_x(angle: float) -> glm.mat4:
    return glm.rotate(glm.mat4(1.0), angle, glm.vec3(1.0, 0.0, 0.0))


def create_rotation_y(angle: float) -> glm.mat4:
    return glm.rotate(glm.mat4(1.0), angle, glm.vec3(0.0, 1.0, 0.0))


def create_rotation_z(angle: float) -> glm.mat4:
    return glm.rotate(glm.mat4(1.0), angle, glm.vec3(0.0, 0.0, 1.0))


def create_transform_3d(pos: glm.vec3, size: glm.vec3, rot: glm.vec3) -> glm.mat4:
    transform = glm.translate(glm.mat4(1.0), pos)
    transform = glm.scale(transform, size)

    transform = glm.rotate(transform, rot.x, glm.vec3(1.0, 0.0, 0.0))
    transform = glm.rotate(transform, rot.y, glm.vec3(0.0, 1.0, 0.0))
    return glm.rotate(transform, rot.z, glm.vec3(0.0, 0.0, 1.0))


def lerp_float(factor: float, x: float, y: float) -> float:
    return (1 - factor) * x + factor * y


def lerp_vector(factor: float, x, y):
    # TODO: Add generic type hint for x, y and return vectors
    if __debug__:
        len_x = len(x.to_list())
        len_y = len(y.to_list())

        if len_x != len_y:
            raise SpykeException(
                'Cannot interpolate vectors with different sizes.')

    values = [lerp_float(factor, _x, _y) for _x, _y in zip(x, y)]
    ctor = getattr(glm, f'vec{len(x)}')

    return ctor(values)
