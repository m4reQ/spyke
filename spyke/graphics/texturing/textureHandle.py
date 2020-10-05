class TextureHandle(object):
    def __init__(self, u: float, v: float, index: float, arrayId: int):
        self.U = u
        self.V = v
        self.Index = index
        self.TexarrayID = arrayId