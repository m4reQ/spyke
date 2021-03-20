import glm as _glm

def CreateTranslation(pos: tuple) -> _glm.mat4:
    return _glm.translate(_glm.mat4(1.0), _glm.vec3(pos))

def CreateScale(size: tuple) -> _glm.mat4:
    return _glm.scale(_glm.mat4(1.0), _glm.vec3(size))

def CreateRotationX(angle: float) -> _glm.mat4:
	return _glm.rotate(_glm.mat4(1.0), angle, _glm.vec3(1.0, 0.0, 0.0))

def CreateRotationY(angle: float) -> _glm.mat4:
	return _glm.rotate(_glm.mat4(1.0), angle, _glm.vec3(0.0, 1.0, 0.0))

def CreateRotationZ(angle: float) -> _glm.mat4:
    return _glm.rotate(_glm.mat4(1.0), angle, _glm.vec3(0.0, 0.0, 1.0))

def CreateTransform3D(pos: _glm.vec3, size: _glm.vec3, rot: _glm.vec3) -> _glm.mat4:
	transform = _glm.translate(_glm.mat4(1.0), pos)
	transform = _glm.scale(transform, size)

	transform = _glm.rotate(transform, rot.x, _glm.vec3(1.0, 0.0, 0.0))
	transform = _glm.rotate(transform, rot.y, _glm.vec3(0.0, 1.0, 0.0))
	return _glm.rotate(transform, rot.z, _glm.vec3(0.0, 0.0, 1.0))