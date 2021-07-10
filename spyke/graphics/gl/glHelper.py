from OpenGL import GL

GLenum = GL.GLenum

def CreateTexture(target: GLenum) -> int:
    _id = GL.GLint()
    GL.glCreateTextures(target, 1, _id)

    return _id.value

def CreateVertexArray() -> int:
    _id = GL.GLint()
    GL.glCreateVertexArrays(1, _id)

    return _id.value

def CreateBuffer() -> int:
    _id = GL.GLint()
    GL.glCreateBuffers(1, _id)

    return _id.value

def CreateFramebuffer() -> int:
    _id = GL.GLint()
    GL.glCreateFramebuffers(1, _id)

    return _id.value