from .aDrawable import ADrawable
from ...constants import _TRIANGLE_MODEL_INDEX

class QuadComponent(ADrawable):
    def __init__(self, material: str):
        super().__init__(material, _TRIANGLE_MODEL_INDEX)