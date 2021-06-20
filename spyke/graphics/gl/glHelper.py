from OpenGL import GL

GLenum = GL.GLenum

class GLHelper:
    @staticmethod
    def CreateTexture(target: GLenum) -> int:
        _id = GL.GLint()
        GL.glCreateTextures(target, 1, _id)

        return _id.value
    
    @staticmethod
    def CreateVertexArray() -> int:
        _id = GL.GLint()
        GL.glCreateVertexArrays(1, _id)

        return _id.value
    
    @staticmethod
    def CreateBuffer() -> int:
        _id = GL.GLint()
        GL.glCreateBuffers(1, _id)

        return _id.value
    
    @staticmethod
    def CreateFramebuffer() -> int:
        _id = GL.GLint()
        GL.glCreateFrameBuffers(1, _id)

        return _id.value