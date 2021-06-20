from .glMarshal import GLMarshal

class GLObject(object):
    def __init__(self):
        self._id = 0
        GLMarshal.AddObjectRef(self)

    def Delete(self, removeRef: bool) -> None:
        if removeRef:
            GLMarshal.RemoveObjectRef(self)
    
    @property
    def ID(self):
        return self._id