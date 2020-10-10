from ..texturing.textureArray import TextureArray
from ..texturing.textureUtils import TextureData
from ..texturing.textureLoader import LoadTexture
from ...debug import Log, LogLevel

class FontManager:
    __TextureWidth = 512
    __TextureHeight = 512
    __MaxFontTextures = 5

    TextureArray = None
    Initialized = False

    @staticmethod
    def Initialize():
        if FontManager.Initialized:
            Log("Font manager already initialized.", LogLevel.Warning)
            return
        
        FontManager.TextureArray = TextureArray(FontManager.__TextureWidth, FontManager.__TextureHeight, FontManager.__MaxFontTextures)

        FontManager.Initialized = True
    
    @staticmethod
    def AddTexture(texData: TextureData):
        return FontManager.TextureArray.UploadTexture(texData)
    
    @staticmethod
    def Use():
        FontManager.TextureArray.Bind()
