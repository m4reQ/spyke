import glm

#region Linear Interpolation
def LerpFloat(factor: float, a: float, b: float) -> float:
    return (factor * a) + ((1 - factor) * b)

def LerpVec2(factor: float, a: glm.vec2, b: glm.vec2) -> glm.vec2:
    _x = (factor * a.x) + ((1 - factor) * b.x)
    _y = (factor * a.y) + ((1 - factor) * b.y)

    return glm.vec2(_x, _y)

def LerpVec3(factor: float, a: glm.vec3, b: glm.vec3) -> glm.vec3:
    _x = (factor * a.x) + ((1 - factor) * b.x)
    _y = (factor * a.y) + ((1 - factor) * b.y)
    _z = (factor * a.z) + ((1 - factor) * b.z)

    return glm.vec3(_x, _y, _z)

def LerpVec4(factor: float, a: glm.vec4, b: glm.vec4) -> glm.vec4:
    _x = (factor * a.x) + ((1 - factor) * b.x)
    _y = (factor * a.y) + ((1 - factor) * b.y)
    _z = (factor * a.z) + ((1 - factor) * b.z)
    _w = (factor * a.w) + ((1 - factor) * b.w)
    
    return glm.vec4(_x, _y, _z, _w)
#endregion
# %%
