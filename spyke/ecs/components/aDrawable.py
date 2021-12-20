class ADrawable:
    __slots__ = ('__weakref__', 'material', 'model_id')
    
    def __init__(self, material: str, model_id: int):
        self.material = material
        self.model_id = model_id