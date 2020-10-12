from .textureUtils import TextureData, IMAGE_FORMAT_MAP
from ...debug import Log, LogLevel, Timer

from PIL import Image

def __LoadTexture(filepath: str):
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

    Log(f"Image '{filepath}' loaded in {Timer.Stop()} seconds.", LogLevel.Info)

    return texData