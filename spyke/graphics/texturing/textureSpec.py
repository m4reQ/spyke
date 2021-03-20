from OpenGL import GL

class TextureSpec(object):
    def __init__(self):
        self.mipmaps = 3
        self.minFilter = GL.GL_LINEAR_MIPMAP_LINEAR
        self.magFilter = GL.GL_LINEAR
        self.wrapMode = GL.GL_REPEAT