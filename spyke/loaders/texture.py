from ..graphics.texturing.textureData import TextureData

from PIL import Image
from OpenGL import GL

_IMAGE_FORMAT_MAP = {
	"JPEG": GL.GL_RGB,
	"JPG": GL.GL_RGB,
	"PNG": GL.GL_RGBA,
	"RGB": GL.GL_RGB,
	"RGBA": GL.GL_RGBA}

def LoadTexture(filepath: str):
	try:
		img = Image.open(filepath)
	except FileNotFoundError:
		raise RuntimeError(f"Cannot find image file: {filepath}.")

	texData = TextureData(img.size[0], img.size[1])

	texData.data = list(img.getdata())
	texData.format = _IMAGE_FORMAT_MAP[img.mode]

	img.close()

	return texData
