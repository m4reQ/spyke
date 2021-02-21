from .textureData import TextureData

from OpenGL import GL

def GetWhiteTexture():
	data = TextureData(1, 1)
	data.data = [255, 255, 255, 255]
	data.minFilter = GL.GL_NEAREST
	data.magFilter = GL.GL_NEAREST
	data.mipLevels = 1
	data.format = GL.GL_RGBA

	return data