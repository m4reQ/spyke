from ..texturing.textureArray import TextureArray
from ..texturing.textureUtils import TextureData
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
    def AddTexture(data: TextureData):
        return FontManager.TextureArray.UploadTexture(data)
    
    @staticmethod
    def Use():
        FontManager.TextureArray.Bind()
