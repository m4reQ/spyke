import glm
from glm import vec2 as Vector2, vec3 as Vector3
from functools import lru_cache

IdentityMatrix4 = glm.mat4(1.0)

QuadVertices = [
	glm.vec4(0.0, 0.0, 0.0, 1.0),
	glm.vec4(0.0, 1.0, 0.0, 1.0),
	glm.vec4(1.0, 1.0, 0.0, 1.0),
	glm.vec4(1.0, 0.0, 0.0, 1.0)]

def CreateTranslation(pos: tuple):
    return glm.translate(glm.mat4(1.0), glm.vec3(pos))

def CreateScale(size: tuple):
    return glm.scale(glm.mat4(1.0), glm.vec3(size))

def CreateRotationZ(angle: float):
    return glm.rotate(glm.mat4(1.0), angle, glm.vec3(0.0, 0.0, 1.0))

def CreateTransform(pos: glm.vec3, size: glm.vec3, angle: float):
	transform = glm.translate(glm.mat4(1.0), pos)
	transform = glm.scale(transform, size)
	return glm.rotate(transform, angle, glm.vec3(0.0, 0.0, 1.0))

@lru_cache
def TransformQuadVertices(transformTuple: tuple):
	transform = glm.mat4(transformTuple[0], transformTuple[1], transformTuple[2], transformTuple[3])
	verts = [
		transform * QuadVertices[0],
		transform * QuadVertices[1],
		transform * QuadVertices[2],
		transform * QuadVertices[3]]
	
	return verts
