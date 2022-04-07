from __future__ import annotations
from uuid import UUID
import numpy as np
from .resource import Resource

class Model(Resource):
    def __init__(self, _id: UUID, filepath: str = ''):
        super().__init__(_id, filepath)

        self.position_data: np.ndarray
        self.index_data: np.ndarray
        self.texture_coords: np.ndarray
        self.vertices_per_instance: int
    
    def _unload(self) -> None:
        super()._unload()