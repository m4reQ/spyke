import glm as _glm

#region Linear Interpolation
def LerpFloat(factor: float, x: float, y: float):
	return (1 - factor) * x + factor * y

def LerpVec2(factor: float, a: _glm.vec2, b: _glm.vec2) -> _glm.vec2:
	_x = LerpFloat(factor, a.x, b.x)
	_y = LerpFloat(factor, a.y, b.y)

	return _glm.vec2(_x, _y)

def LerpVec3(factor: float, a: _glm.vec3, b: _glm.vec3) -> _glm.vec3:
	_x = LerpFloat(factor, a.x, b.x)
	_y = LerpFloat(factor, a.y, b.y)
	_z = LerpFloat(factor, a.z, b.z)

	return _glm.vec3(_x, _y, _z)

def LerpVec4(factor: float, a: _glm.vec4, b: _glm.vec4) -> _glm.vec4:
	_x = LerpFloat(factor, a.x, b.x)
	_y = LerpFloat(factor, a.y, b.y)
	_z = LerpFloat(factor, a.z, b.z)
	_w = LerpFloat(factor, a.w, b.w)
	
	return _glm.vec4(_x, _y, _z, _w)
#endregion