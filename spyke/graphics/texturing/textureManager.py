from .textureArray import TextureArray
from .textureHandle import TextureHandle
from .textureLoader import LoadTexture
from ...debug import Log, LogLevel
from ...utils import Static

class TextureManager(Static):
    CreateIfNotPresent = True
    DefaultLayersCount = 10

    __TextureArrays = []

    def CreateTextureArray(width: int, height: int, layers: int) -> None:
        TextureManager.__TextureArrays.append(TextureArray(width, height, layers))
    
    def LoadTexture(filepath: int) -> TextureHandle:
        texData = LoadTexture(filepath)
        try:
            arr = next((x for x in TextureManager.__TextureArrays if texData.Width <= x.Width and texData.Height <= x.Height and x.IsAccepting))
        except StopIteration:
            if TextureManager.CreateIfNotPresent:
                Log("Texture manager automatically created new texture array.", LogLevel.Warning)
                arr = TextureArray(texData.Width, texData.Height, TextureManager.DefaultLayersCount)
                TextureManager.__TextureArrays.append(arr)
            else:
                raise RuntimeError("Cannot find suitable texture array to load texture into.")

        return arr.UploadTexture(texData)