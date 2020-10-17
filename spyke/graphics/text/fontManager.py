from ..texturing.textureArray import TextureArray
from ..texturing.textureUtils import TextureData, TextureHandle
from ..texturing.textureManager import TextureManager
from ...debug import Log, LogLevel

class FontManager:
    __TextureWidth = 512
    __TextureHeight = 512
    __MaxFontTextures = 5

    TextureArray = None
    Initialized = False

    @staticmethod
    def Initialize() -> None:
        if FontManager.Initialized:
            Log("Font manager already initialized.", LogLevel.Warning)
            return
        
        FontManager.TextureArray = TextureManager.CreateTextureArray(FontManager.__TextureWidth, FontManager.__TextureHeight, FontManager.__MaxFontTextures)

        FontManager.Initialized = True
    
    @staticmethod
    def AddTexture(texData: TextureData) -> TextureHandle:
        return TextureManager.UploadTexture(texData, FontManager.TextureArray)
    
    @staticmethod
    def Use() -> None:
        TextureManager.GetArray(FontManager.TextureArray).Bind()
