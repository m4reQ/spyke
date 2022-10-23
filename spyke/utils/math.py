import math
import typing as t

import glm
from glm import vec2 as Vector2, vec3 as Vector3, vec4 as Vector4, mat4 as Matrix4

__all__ = [
    'Vector2',
    'Vector3',
    'Vector4',
    'Matrix4',
    'lerp_float',
    'lerp_vector',
    'get_closest_factors'
]

def lerp_float(factor: float, x: float, y: float) -> float:
    return (1 - factor) * x + factor * y

_VT = t.TypeVar('_VT', glm.vec2, glm.vec3, glm.vec4)
def lerp_vector(factor: float, x: _VT, y: _VT) -> _VT:
    if len(x) != len(y):
        raise ValueError('Cannot interpolate vectors with different sizes.')

    values = [lerp_float(factor, _x, _y) for _x, _y in zip(x, y)]
    ctor = getattr(glm, f'vec{len(x)}')

    return ctor(values)

def get_closest_factors(num: int) -> tuple[int, int]:
    test_num = int(math.sqrt(num))
    while num % test_num != 0:
        test_num -= 1

    return (test_num, num // test_num)
