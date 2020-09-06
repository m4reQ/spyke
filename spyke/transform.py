import glm

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