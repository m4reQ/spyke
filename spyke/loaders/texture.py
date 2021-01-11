from ..graphics.texturing.textureUtils import IMAGE_FORMAT_MAP
from ..graphics.texturing.textureData import TextureData

from PIL import Image

def LoadTexture(filepath: str):
	try:
		img = Image.open(filepath)
	except FileNotFoundError:
		raise RuntimeError(f"Cannot find image file: {filepath}.")

	texData = TextureData(img.size[0], img.size[1])

	texData.data = list(img.getdata())
	texData.format = IMAGE_FORMAT_MAP[img.mode]

	img.close()

	return texData