from ..graphics.texturing.texture import TextureData
from ..constants import _IMAGE_FORMAT_MAP

from PIL import Image
from OpenGL import GL

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
