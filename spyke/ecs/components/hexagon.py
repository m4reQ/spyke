from .aDrawable import ADrawable
from ...constants import _HEXAGON_MODEL_INDEX

class QuadComponent(ADrawable):
    def __init__(self, material: str):
        super().__init__(material, _HEXAGON_MODEL_INDEX)