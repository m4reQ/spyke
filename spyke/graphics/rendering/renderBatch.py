from ....utils import GL_FLOAT_SIZE

class RenderBatch(object):
    def __init__(self, maxSize):
        self.maxSize = maxSize
        self.texarrayIndex = -1
        self.data = []
        self.dataSize = 0
    
    def AddData(self, data):
        if self.dataSize + len(data) * GL_FLOAT_SIZE > self.maxSize:
            raise RuntimeError("Cannot store more data in render batch.")

        self.data.extend(data)
        self.dataSize += len(data) * GL_FLOAT_SIZE
    
    @property
    def IsAccepting(self):
        return self.dataSize < self.maxSize
    
    @property
    def Size(self):
        return self.dataSize