from .textureUtils import TextureData, IMAGE_FORMAT_MAP
from .ogl.textureArray import TextureArray
from ..debug import Log, LogLevel

from time import perf_counter
from PIL import Image

def __LoadTexture(filepath: str):
    start = perf_counter()

    try:
        img = Image.open(filepath)
    except FileNotFoundError:
        raise RuntimeError(f"Cannot find image file: {filepath}.")

    texData = TextureData()
    texData.Width = img.size[0]
    texData.Height = img.size[1]

    texData.Data = list(img.getdata())
    texData.TextureType = IMAGE_FORMAT_MAP[img.mode]

    texData.ImageName = filepath

    img.close()

    Log(f"Image '{filepath}' loaded in {perf_counter() - start} seconds.", LogLevel.Info)

    return texData

def UploadTexture(filename: str, textureArray: TextureArray):
    return textureArray.UploadTexture(__LoadTexture(filename))

def LoadTexture(filename: str):
    return __LoadTexture(filename)