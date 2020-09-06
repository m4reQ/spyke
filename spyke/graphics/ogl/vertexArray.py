from ...utils import GetGLTypeSize, GetPointer, ObjectManager

from OpenGL import GL

class VertexArrayLayout:
    def __init__(self, index, count, type, normalized):
        self.Index = index
        self.Count = count
        self.Type = type
        self.IsNormalized = normalized

class VertexArray(object):
    def __init__(self, vertexSize):
        self.__vertexSize = vertexSize

        self.__id = GL.glGenVertexArrays(1)
        self.__offset = 0

        ObjectManager.AddObject(self)

    def AddLayout(self, layout: VertexArrayLayout):
        GL.glVertexAttribPointer(layout.Index, layout.Count, layout.Type, layout.IsNormalized, self.__vertexSize, GetPointer(self.__offset))
        GL.glEnableVertexAttribArray(layout.Index)
        
        self.__offset += GetGLTypeSize(layout.Type) * layout.Count
    
    def AddLayouts(self, layouts: list):
        for layout in layouts:
            self.AddLayout(layout)

    def Bind(self):
        GL.glBindVertexArray(self.__id)
    
    def Delete(self):
        GL.glDeleteVertexArrays(1, [self.__id])
    
    @property
    def ID(self):
        return self.__id