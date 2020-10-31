import glm
from glm import vec2 as Vector2, vec3 as Vector3, mat4 as Matrix4, vec4 as Vector4
from functools import lru_cache

IdentityMatrix4 = glm.mat4(1.0)

QuadVertices = [
	glm.vec4(0.0, 0.0, 0.0, 1.0),
	glm.vec4(0.0, 1.0, 0.0, 1.0),
	glm.vec4(1.0, 1.0, 0.0, 1.0),
	glm.vec4(1.0, 0.0, 0.0, 1.0)]

def GetQuadIndexData(count: int) -> list:
	data = []

	offset = 0
	i = 0
	while i < count:
		data.extend([
			0 + offset,
			1 + offset,
			2 + offset,
			2 + offset,
			3 + offset,
			0 + offset])
		
		offset += 4
		i += 6
	
	return data

#region Transform
def CreateTranslation(pos: tuple) -> glm.mat4:
    return glm.translate(glm.mat4(1.0), glm.vec3(pos))

def CreateScale(size: tuple) -> glm.mat4:
    return glm.scale(glm.mat4(1.0), glm.vec3(size))

def CreateRotationZ(angle: float) -> glm.mat4:
    return glm.rotate(glm.mat4(1.0), angle, glm.vec3(0.0, 0.0, 1.0))

def CreateTransform3D(pos: glm.vec3, size: glm.vec2, angle: float) -> glm.mat4:
	transform = glm.translate(glm.mat4(1.0), pos)
	transform = glm.scale(transform, glm.vec3(size, 0.0))
	return glm.rotate(transform, angle, glm.vec3(0.0, 0.0, 1.0))

@lru_cache
def TransformQuadVertices(transformTuple: tuple) -> list:
	transform = glm.mat4(transformTuple[0], transformTuple[1], transformTuple[2], transformTuple[3])
	return [
		transform * QuadVertices[0],
		transform * QuadVertices[1],
		transform * QuadVertices[2],
		transform * QuadVertices[3]]
#endregion