import glm

#region Linear Interpolation
def LerpFloat(factor: float, x: float, y: float):
	return (1 - factor) * x + factor * y

def LerpVec2(factor: float, a: glm.vec2, b: glm.vec2) -> glm.vec2:
	_x = LerpFloat(factor, a.x, b.x)
	_y = LerpFloat(factor, a.y, b.y)

	return glm.vec2(_x, _y)

def LerpVec3(factor: float, a: glm.vec3, b: glm.vec3) -> glm.vec3:
	_x = LerpFloat(factor, a.x, b.x)
	_y = LerpFloat(factor, a.y, b.y)
	_z = LerpFloat(factor, a.z, b.z)

	return glm.vec3(_x, _y, _z)

def LerpVec4(factor: float, a: glm.vec4, b: glm.vec4) -> glm.vec4:
	_x = LerpFloat(factor, a.x, b.x)
	_y = LerpFloat(factor, a.y, b.y)
	_z = LerpFloat(factor, a.z, b.z)
	_w = LerpFloat(factor, a.w, b.w)
	
	return glm.vec4(_x, _y, _z, _w)
#endregion