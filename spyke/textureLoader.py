#region Import
from .utils import Static, Timer
from .debug import Log, LogLevel
from .graphics import TextureData, TextureHandle, TextureArray
from .graphics.texturing.textureUtils import IMAGE_FORMAT_MAP

from PIL import Image
#endregion

class TextureLoader(Static):
	def LoadTexture(filepath: str, texArray: TextureArray) -> TextureHandle:
		Timer.Start()

		try:
			img = Image.open(filepath)
		except FileNotFoundError:
			raise RuntimeError(f"Cannot find image file: {filepath}.")

		texData = TextureData()
		texData.Width = img.size[0]
		texData.Height = img.size[1]

		texData.Data = list(img.getdata())
		texData.TextureType = IMAGE_FORMAT_MAP[img.mode]

		img.close()

		texData.ImageName = filepath
		handle = texArray.UploadTexture(texData)

		Log(f"Image '{filepath}' loaded in {Timer.Stop()} seconds.", LogLevel.Info)

		return handle