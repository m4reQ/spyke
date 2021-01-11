from OpenGL import GL

class TextureData(object):
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.data = []
		self.format = GL.GL_RGB
		self.mipLevels = 4
		self.minFilter = GL.GL_LINEAR_MIPMAP_LINEAR
		self.magFilter = GL.GL_LINEAR