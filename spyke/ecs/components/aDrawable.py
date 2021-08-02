from ...autoslot import Slots

class ADrawable(Slots):
    __slots__ = ("__weakref__", )
    
    def __init__(self, material: str, modelId: int):
        self.material = material
        self.modelId = modelId